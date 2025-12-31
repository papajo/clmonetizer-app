from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
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
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Starts a scraping job in the background.
    """
    # Validate URL format
    if not request.url or not isinstance(request.url, str) or not request.url.strip():
        raise HTTPException(status_code=422, detail="URL is required and must be a non-empty string")
    
    url = request.url.strip()
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=422, detail="URL must start with http:// or https://")
    
    background_tasks.add_task(run_scrape_job, url)
    return {"message": "Scraping started", "url": url}

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
                        source="craigslist"
                    )
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
                        
                        # Trigger AI Analysis
                        # In a real app, this might be a separate worker queue
                        try:
                            analysis = await ai_service.analyze_arbitrage({**item, **details})
                            
                            listing.is_arbitrage_opportunity = analysis.is_arbitrage_opportunity
                            listing.profit_potential = analysis.profit_potential
                            listing.analysis_json = analysis.model_dump()
                            
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

@router.get("/listings")
def get_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    listings = db.query(Listing).offset(skip).limit(limit).all()
    return listings

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
    
    return {
        "total_listings": total_listings,
        "opportunities": opportunities,
        "total_leads": total_leads,
        "total_profit_potential": float(profit_result) if profit_result else 0.0
    }
