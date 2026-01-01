from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional
import os
from ..database import get_db, SessionLocal
from ..models import Listing, Lead
from ..services.scraper_service import scraper_service
from ..services.ai_service import ai_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ScrapeRequest(BaseModel):
    url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://newyork.craigslist.org/search/cto"
            }
        }

@router.post("/scrape")
async def start_scrape(
    background_tasks: BackgroundTasks,
    request: Optional[ScrapeRequest] = None,
    url: Optional[str] = Query(None, description="URL to scrape (alternative to request body)"),
):
    """
    Starts a scraping job in the background.
    Accepts URL either in request body as JSON: {"url": "..."} or as query parameter: ?url=...
    """
    # Get URL from either request body or query parameter
    url_value = None
    if request and request.url:
        url_value = request.url
    elif url:
        url_value = url
    
    if not url_value:
        raise HTTPException(
            status_code=422, 
            detail="URL is required. Provide it either in request body as {'url': '...'} or as query parameter ?url=..."
        )
    
    # Validate URL format
    if not isinstance(url_value, str) or not url_value.strip():
        raise HTTPException(status_code=422, detail="URL must be a non-empty string")
    
    url_value = url_value.strip()
    if not url_value.startswith(('http://', 'https://')):
        raise HTTPException(status_code=422, detail="URL must start with http:// or https://")
    
    # Queue the background task and return immediately
    background_tasks.add_task(run_scrape_job, url_value)
    logger.info(f"Scrape job queued for URL: {url_value}")
    return {"message": "Scraping started", "url": url_value}

async def run_scrape_job(url: str):
    """
    Background task to scrape Craigslist listings.
    Creates its own database session since the endpoint's session closes when the request completes.
    """
    # Create a new database session for this background task
    db = SessionLocal()
    logger.info(f"Starting background scrape for {url}")
    listings_processed = 0
    listings_added = 0
    errors = []
    
    try:
        listings = await scraper_service.scrape_category(url)
        logger.info(f"Scraper returned {len(listings)} listings to process")
        
        if not listings:
            logger.warning(f"No listings found for URL: {url}. This might indicate:")
            logger.warning("1. The page structure has changed")
            logger.warning("2. The URL format is not supported")
            logger.warning("3. The page requires authentication or has blocking")
            return
        
        for item in listings:
            listings_processed += 1
            try:
                # Check if listing exists
                exists = db.query(Listing).filter(Listing.url == item['url']).first()
                if not exists:
                    # Parse price safely
                    price = None
                    if item.get('price'):
                        try:
                            price_str = str(item['price']).replace('$', '').replace(',', '').strip()
                            price = float(price_str) if price_str else None
                        except (ValueError, AttributeError):
                            price = None
                    
                    listing = Listing(
                        title=item.get('title', 'Untitled'),
                        url=item['url'],
                        price=price,
                        source="craigslist",
                        is_free_item=item.get('is_free', False)
                    db.add(listing)
                    db.commit()
                    db.refresh(listing)
                    
                    # Scrape detailed information
                    try:
                        details = await scraper_service.scrape_listing_details(item['url'])
                        
                        # Update listing with details
                        if details.get('description'):
                            listing.description = details.get('description')
                        if details.get('location'):
                            listing.location = details.get('location')
                        if details.get('mileage'):
                            try:
                                listing.mileage = int(str(details.get('mileage')).replace(',', '').replace('mi', '').strip())
                            except (ValueError, AttributeError):
                                pass
                        
                        db.commit()
                        
                        # Trigger AI Analysis (enhanced with PDF strategies)
                        # In a real app, this might be a separate worker queue
                        try:
                            listing_data = {**item, **details}
                            
                            # Main arbitrage analysis
                            analysis = await ai_service.analyze_arbitrage(listing_data)
                            
                            listing.is_arbitrage_opportunity = analysis.is_arbitrage_opportunity
                            listing.profit_potential = analysis.profit_potential
                            listing.analysis_json = analysis.model_dump()
                            
                            # Store enhanced fields from analysis
                            if hasattr(analysis, 'category'):
                                listing.category = analysis.category
                            if hasattr(analysis, 'market_demand'):
                                listing.market_demand = analysis.market_demand
                            if hasattr(analysis, 'recommended_price'):
                                listing.recommended_price = analysis.recommended_price
                            
                            # Ad quality analysis
                            try:
                                ad_quality = await ai_service.analyze_ad_quality(listing_data)
                                listing.ad_quality_score = ad_quality.overall_score
                                listing.ad_quality_json = ad_quality.model_dump()
                            except Exception as ad_error:
                                logger.warning(f"Ad quality analysis failed: {ad_error}")
                            
                            # Market research analysis
                            try:
                                market_research = await ai_service.analyze_market_research(listing_data)
                                listing.market_research_json = market_research.model_dump()
                            except Exception as mr_error:
                                logger.warning(f"Market research analysis failed: {mr_error}")
                            
                            if analysis.is_arbitrage_opportunity:
                                logger.info(f"Arbitrage opportunity found: {listing.title}")
                            
                            db.commit()
                        except Exception as ai_error:
                            logger.error(f"AI analysis failed for listing {listing.id}: {ai_error}")
                            # Continue processing other listings even if AI fails
                            
                    except Exception as detail_error:
                        error_msg = f"Failed to scrape details for {item.get('url', 'unknown')}: {detail_error}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        # Continue processing other listings
                    else:
                        listings_added += 1
            except Exception as item_error:
                error_msg = f"Error processing listing {item.get('url', 'unknown')}: {item_error}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                # Continue with next listing
                
    except Exception as e:
        logger.error(f"Scrape job failed for {url}: {e}", exc_info=True)
        errors.append(f"Fatal error: {str(e)}")
    finally:
        logger.info(f"Scrape job completed for {url}: {listings_added} added, {listings_processed} processed, {len(errors)} errors")
        if errors:
            logger.warning(f"Errors encountered: {errors[:5]}")  # Log first 5 errors
        # Close the database session
        db.close()

@router.post("/listings/reanalyze")
async def reanalyze_listings(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Re-analyze all existing listings that haven't been marked as opportunities.
    Useful after setting up the OpenAI API key.
    """
    # Get listings that haven't been analyzed or failed analysis
    listings = db.query(Listing).filter(
        (Listing.is_arbitrage_opportunity == False) | (Listing.is_arbitrage_opportunity.is_(None))
    ).all()
    
    count = len(listings)
    logger.info(f"Queueing re-analysis for {count} listings")
    
    # Queue background task to re-analyze
    background_tasks.add_task(reanalyze_listings_job, [l.id for l in listings])
    
    return {
        "message": f"Re-analysis queued for {count} listings",
        "count": count
    }

async def reanalyze_listings_job(listing_ids: list[int]):
    """
    Background task to re-analyze listings.
    """
    db = SessionLocal()
    logger.info(f"Starting re-analysis for {len(listing_ids)} listings")
    analyzed = 0
    opportunities_found = 0
    
    try:
        for listing_id in listing_ids:
            try:
                listing = db.query(Listing).filter(Listing.id == listing_id).first()
                if not listing:
                    continue
                
                # Prepare listing data for analysis
                listing_data = {
                    "title": listing.title or "Untitled",
                    "price": listing.price,
                    "description": listing.description or "",
                    "location": listing.location or "",
                    "url": listing.url
                }
                
                # Run AI analysis
                analysis = await ai_service.analyze_arbitrage(listing_data)
                
                # Update listing
                listing.is_arbitrage_opportunity = analysis.is_arbitrage_opportunity
                listing.profit_potential = analysis.profit_potential
                listing.analysis_json = analysis.model_dump()
                
                db.commit()
                analyzed += 1
                
                if analysis.is_arbitrage_opportunity:
                    opportunities_found += 1
                    logger.info(f"Opportunity found: {listing.title}")
                    
            except Exception as e:
                logger.error(f"Error re-analyzing listing {listing_id}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Re-analysis job failed: {e}", exc_info=True)
    finally:
        logger.info(f"Re-analysis completed: {analyzed} analyzed, {opportunities_found} opportunities found")
        db.close()

@router.get("/listings")
def get_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    listings = db.query(Listing).order_by(Listing.date_scraped.desc()).offset(skip).limit(limit).all()
    return listings

@router.get("/listings/recent")
def get_recent_listings(limit: int = 10, db: Session = Depends(get_db)):
    """Get recently scraped listings, ordered by most recent first."""
    listings = db.query(Listing).order_by(Listing.date_scraped.desc()).limit(limit).all()
    return {
        "count": len(listings),
        "listings": listings
    }

@router.get("/listings/count")
def get_listings_count(db: Session = Depends(get_db)):
    """Get total count of listings in database."""
    count = db.query(Listing).count()
    return {"count": count}

@router.get("/listings/opportunities")
def get_opportunities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get listings that are arbitrage opportunities."""
    listings = db.query(Listing).filter(
        Listing.is_arbitrage_opportunity == True
    ).offset(skip).limit(limit).all()
    return listings

@router.get("/leads")
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).all()
    return leads

@router.get("/listings/free")
def get_free_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get listings from the 'free' section that can be resold for profit."""
    listings = db.query(Listing).filter(
        Listing.is_free_item == True
    ).order_by(Listing.date_scraped.desc()).offset(skip).limit(limit).all()
    return listings

@router.get("/listings/by-category")
def get_listings_by_category(
    category: str = Query(..., description="Category to filter by (e.g., 'car', 'appliance', 'furniture')"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get listings filtered by category."""
    listings = db.query(Listing).filter(
        Listing.category == category
    ).order_by(Listing.date_scraped.desc()).offset(skip).limit(limit).all()
    return listings

@router.get("/listings/high-quality-ads")
def get_high_quality_ads(
    min_score: float = Query(70.0, description="Minimum ad quality score (0-100)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get listings with high ad quality scores."""
    listings = db.query(Listing).filter(
        Listing.ad_quality_score >= min_score
    ).order_by(Listing.ad_quality_score.desc()).offset(skip).limit(limit).all()
    return listings

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_listings = db.query(Listing).count()
    opportunities = db.query(Listing).filter(Listing.is_arbitrage_opportunity == True).count()
    total_leads = db.query(Lead).count()
    
    # Calculate total profit potential
    profit_result = db.query(Listing).filter(
        Listing.profit_potential.isnot(None)
    ).with_entities(
        func.sum(Listing.profit_potential)
    ).scalar() or 0
    
    # Get most recent listing date
    most_recent = db.query(Listing).order_by(Listing.date_scraped.desc()).first()
    most_recent_date = most_recent.date_scraped.isoformat() if most_recent else None
    
    # Check if AI service is configured (Gemini or OpenAI)
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    ai_configured = (
        (gemini_key and not gemini_key.startswith("dummy")) or
        (openai_key and not openai_key.startswith("sk-dummy") and openai_key != "")
    )
    
    return {
        "total_listings": total_listings,
        "opportunities": opportunities,
        "total_leads": total_leads,
        "total_profit_potential": float(profit_result) if profit_result else 0.0,
        "most_recent_scrape": most_recent_date,
        "ai_configured": ai_configured
    }
