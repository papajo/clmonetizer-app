import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Load .env file
load_dotenv()

# Try to import OpenAI and Gemini
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class AnalysisResult(BaseModel):
    is_arbitrage_opportunity: bool = Field(description="True if the item is underpriced and can be flipped.")
    profit_potential: float = Field(description="Estimated profit in USD.")
    reasoning: str = Field(description="Explanation of why this is a good deal.")
    suggested_platform: str = Field(description="Where to resell: 'Facebook Marketplace', 'eBay', etc.")
    category: str = Field(default="", description="Item category: 'car', 'appliance', 'furniture', 'electronics', etc.")
    market_demand: str = Field(default="", description="Market demand assessment: 'high', 'medium', 'low'")
    recommended_price: float = Field(default=0.0, description="Recommended resale price based on market research")

class AdQualityScore(BaseModel):
    overall_score: float = Field(description="Overall ad quality score 0-100")
    has_good_title: bool = Field(description="Title is clear, specific, and includes key details")
    has_detailed_description: bool = Field(description="Description is comprehensive and informative")
    has_photos: bool = Field(description="Ad includes photos")
    pricing_appropriate: bool = Field(description="Price is competitive and realistic")
    suggestions: str = Field(description="Suggestions for improving the ad based on best practices")

class MarketResearch(BaseModel):
    competition_level: str = Field(description="Competition level: 'high', 'medium', 'low'")
    average_market_price: float = Field(description="Average market price for similar items")
    price_competitiveness: str = Field(description="How competitive the price is: 'very competitive', 'competitive', 'overpriced'")
    demand_level: str = Field(description="Demand level: 'high', 'medium', 'low'")
    best_selling_season: str = Field(default="", description="Best time of year to sell this item")
    top_profitable_categories: list = Field(default_factory=list, description="Top profitable categories from the PDF")

class LeadResult(BaseModel):
    is_lead: bool = Field(description="True if this is a 'wanted' ad or a service lead.")
    lead_type: str = Field(description="Type of lead: 'wanted', 'service', 'other'")
    confidence: float = Field(description="Confidence score 0.0 to 1.0")

class AIService:
    def __init__(self):
        # Try Gemini first (often free/cheaper), then OpenAI
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        self.llm = None
        self.api_key_configured = False
        self.provider = None
        
        # Prefer OpenAI if both are available (more reliable)
        # Try OpenAI first if available
        if OPENAI_AVAILABLE and openai_key and not openai_key.startswith("sk-dummy") and openai_key != "":
            try:
                self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, api_key=openai_key)
                self.api_key_configured = True
                self.provider = "openai"
                print("✅ Using OpenAI API for AI analysis")
            except Exception as e:
                print(f"⚠️  Failed to initialize OpenAI: {e}")
        
        # Fallback to Gemini if OpenAI not available
        if not self.api_key_configured and GEMINI_AVAILABLE and gemini_key and not gemini_key.startswith("dummy"):
            try:
                # Try different model names - the correct one depends on API version
                model_names = ["gemini-pro", "models/gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"]
                gemini_initialized = False
                
                for model_name in model_names:
                    try:
                        self.llm = ChatGoogleGenerativeAI(
                            model=model_name,
                            google_api_key=gemini_key,
                            temperature=0
                        )
                        self.api_key_configured = True
                        self.provider = "gemini"
                        print(f"✅ Using Gemini API ({model_name}) for AI analysis")
                        gemini_initialized = True
                        break
                    except Exception as model_error:
                        if "404" in str(model_error) or "NOT_FOUND" in str(model_error):
                            continue
                        else:
                            raise model_error
                
                if not gemini_initialized:
                    print(f"⚠️  Gemini models not available with current API key.")
            except Exception as e:
                print(f"⚠️  Failed to initialize Gemini: {e}")
            try:
                self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, api_key=openai_key)
                self.api_key_configured = True
                self.provider = "openai"
                print("✅ Using OpenAI API for AI analysis")
            except Exception as e:
                print(f"⚠️  Failed to initialize OpenAI: {e}")
        
        if not self.api_key_configured:
            print("⚠️  No AI API key configured. Set GEMINI_API_KEY or OPENAI_API_KEY in .env file")

    async def analyze_arbitrage(self, listing_data: dict) -> AnalysisResult:
        """
        Analyzes a listing to determine if it's a good arbitrage opportunity.
        """
        # Check if API key is configured
        if not self.api_key_configured or self.llm is None:
            return AnalysisResult(
                is_arbitrage_opportunity=False,
                profit_potential=0,
                reasoning="AI API key not configured. Please set GEMINI_API_KEY (recommended, free tier available) or OPENAI_API_KEY in .env file. Get Gemini key at https://makersuite.google.com/app/apikey or OpenAI key at https://platform.openai.com/account/api-keys",
                suggested_platform="None"
            )
        
        parser = PydanticOutputParser(pydantic_object=AnalysisResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert flipper and market analyst specializing in identifying arbitrage opportunities on Craigslist, based on proven strategies from successful sellers.

Your task is to analyze listings and determine if they represent profitable arbitrage opportunities. Consider:

CATEGORY-SPECIFIC PROFITABILITY (from proven strategies):
- Cars: Highest profit margin ($5000-$100,000 range), especially if you can get at half price and fix minor issues
- Appliances: High demand, good supply, 1/4 to 1/3 of new price is typical market value
- Furniture: High-end solid wood furniture is in high demand (beds, chairs, dining tables, desks, mirrors, couches)
- Electronics: High-end items sell well, especially if barely used
- Bikes/Motorbikes: Seasonal pricing - buy in winter, sell in summer for profit
- Power tools/Equipment: Large supply, especially during fire-sales when dealers change professions
- Mobile Phones: Large supply due to frequent upgrades, high demand for replacements

MARKET ANALYSIS:
- Current market value of similar items
- Condition and description quality
- Price competitiveness (should be 1/4 to 1/3 of new price for appliances, half price for cars)
- Resale potential on platforms like Facebook Marketplace, eBay, OfferUp
- Estimated profit after fees and time investment
- Market demand (high/medium/low)
- Competition level in the market

PRICING STRATEGY:
- For appliances: Market typically 1/4 to 1/3 of new price
- For cars: Look for deals at half price, potential to earn thousands per car
- Inflate price slightly (10-20%) to allow for negotiation while still being competitive

Only flag items as opportunities if the profit potential is significant (typically $50+ for smaller items, $500+ for cars/appliances)."""),
            ("user", """Analyze this Craigslist listing for arbitrage potential:

Title: {title}
Price: {price}
Description: {description}
Location: {location}
Additional Details: {additional}

{format_instructions}""")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "title": listing_data.get("title", "N/A"),
                "price": listing_data.get("price", "N/A"),
                "description": listing_data.get("description", listing_data.get("body", "N/A")),
                "location": listing_data.get("location", "N/A"),
                "additional": json.dumps({k: v for k, v in listing_data.items() if k not in ["title", "price", "description", "body", "location"]}, indent=2),
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "401" in error_msg or "invalid_api_key" in error_msg.lower() or "api_key" in error_msg.lower():
                provider_name = "Gemini" if self.provider == "gemini" else "OpenAI"
                error_msg = f"Invalid {provider_name} API key. Please check your API key in .env file."
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                provider_name = "Gemini" if self.provider == "gemini" else "OpenAI"
                error_msg = f"{provider_name} API rate limit exceeded. Please try again later."
            else:
                error_msg = f"AI analysis error ({self.provider or 'unknown'}): {error_msg}"
            
            print(f"Error in AI analysis: {e}")
            return AnalysisResult(
                is_arbitrage_opportunity=False, 
                profit_potential=0, 
                reasoning=error_msg, 
                suggested_platform="None"
            )

    async def analyze_ad_quality(self, listing_data: dict) -> AdQualityScore:
        """
        Analyzes ad quality based on best practices from the PDF.
        """
        if not self.api_key_configured or self.llm is None:
            return AdQualityScore(
                overall_score=0,
                has_good_title=False,
                has_detailed_description=False,
                has_photos=False,
                pricing_appropriate=False,
                suggestions="AI API key not configured"
            )
        
        parser = PydanticOutputParser(pydantic_object=AdQualityScore)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at evaluating Craigslist ad quality based on proven best practices.

Evaluate ads based on these criteria from successful sellers:

TITLE QUALITY:
- Should be short and to the point
- Include item name, brand (if applicable), and price
- Should NOT include negative details (save those for description)
- Should be accurate and not misleading

DESCRIPTION QUALITY:
- Should be detailed and comprehensive
- Include: model, make, brand, age, condition, any issues or malfunctions
- Mention if item works well or what's not working
- Include if item is clean or needs cleaning
- Should NOT include: email address, address, personal info, "need to sell quickly"
- More information = fewer queries from buyers

PHOTOS:
- Essential for sales
- Should have at least one photo
- Multiple angles are better
- Clean background, well-lit
- Avoid extreme close-ups that highlight flaws

PRICING:
- Should be realistic (not expecting full retail price)
- Competitive with market (check garage sales, eBay for reference)
- Can be slightly inflated (10-20%) to allow negotiation
- Should reflect condition accurately"""),
            ("user", """Evaluate the quality of this Craigslist ad:

Title: {title}
Price: {price}
Description: {description}
Has Photos: {has_photos}

{format_instructions}""")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "title": listing_data.get("title", "N/A"),
                "price": listing_data.get("price", "N/A"),
                "description": listing_data.get("description", listing_data.get("body", "")),
                "has_photos": "yes" if listing_data.get("has_images") or listing_data.get("images") else "unknown",
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"Error in ad quality analysis: {e}")
            return AdQualityScore(
                overall_score=0,
                has_good_title=False,
                has_detailed_description=False,
                has_photos=False,
                pricing_appropriate=False,
                suggestions=f"Error analyzing ad quality: {str(e)}"
            )

    async def analyze_market_research(self, listing_data: dict) -> MarketResearch:
        """
        Performs market research analysis based on the listing.
        """
        if not self.api_key_configured or self.llm is None:
            return MarketResearch(
                competition_level="unknown",
                average_market_price=0.0,
                price_competitiveness="unknown",
                demand_level="unknown",
                best_selling_season="",
                top_profitable_categories=[]
            )
        
        parser = PydanticOutputParser(pydantic_object=MarketResearch)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a market research expert specializing in Craigslist arbitrage opportunities.

Analyze market conditions based on proven strategies:

TOP PROFITABLE CATEGORIES (in order):
1. Cars - Highest profit margin ($5000-$100,000 range)
2. Electrical devices/appliances - High demand and supply
3. Motorbikes/Scooters - Seasonal (buy winter, sell summer)
4. Bikes - Good profit after repairs
5. Furniture - High-end solid wood in high demand
6. Electronic items - High-end items sell well
7. Computers - Good if you can repair
8. Yard tools - Profitable if you can repair small engines
9. Power equipment/tools - Large supply, fire-sales common
10. Mobile phones - Large supply, high demand

MARKET ANALYSIS:
- Competition: Check how many similar listings exist (high/medium/low)
- Average market price: Typical price for similar items in good condition
- Price competitiveness: Compare listing price to market average
- Demand: Based on category and item type (high/medium/low)
- Best selling season: When is this item most in demand?"""),
            ("user", """Perform market research for this listing:

Title: {title}
Price: {price}
Description: {description}
Category: {category}

{format_instructions}""")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "title": listing_data.get("title", "N/A"),
                "price": listing_data.get("price", "N/A"),
                "description": listing_data.get("description", listing_data.get("body", "")),
                "category": listing_data.get("category", "general"),
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"Error in market research: {e}")
            return MarketResearch(
                competition_level="unknown",
                average_market_price=0.0,
                price_competitiveness="unknown",
                demand_level="unknown",
                best_selling_season="",
                top_profitable_categories=[]
            )

    async def analyze_lead(self, listing_data: dict) -> LeadResult:
        """
        Analyzes if a listing is a lead (wanted item, service needed).
        """
        parser = PydanticOutputParser(pydantic_object=LeadResult)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a lead generation expert specializing in identifying business opportunities from Craigslist listings.
            
Identify if a listing represents a lead opportunity:
- "wanted": Someone is looking to buy something (you might have it or can source it)
- "service": Someone needs a service (you might provide it or know someone who does)
- "other": Other types of business opportunities

Only mark as a lead if there's a clear business opportunity with reasonable confidence."""),
            ("user", """Analyze this listing to determine if it's a lead opportunity:

Title: {title}
Description: {description}
Category: {category}

{format_instructions}""")
        ])
        
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "title": listing_data.get("title", "N/A"),
                "description": listing_data.get("description", listing_data.get("body", "N/A")),
                "category": listing_data.get("category", "N/A"),
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            print(f"Error in lead analysis: {e}")
            return LeadResult(is_lead=False, lead_type="error", confidence=0.0)

ai_service = AIService()
