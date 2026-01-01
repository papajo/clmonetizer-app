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
            ("system", """You are an expert flipper and market analyst specializing in identifying arbitrage opportunities on Craigslist.
            
Your task is to analyze listings and determine if they represent profitable arbitrage opportunities. Consider:
- Current market value of similar items
- Condition and description quality
- Price competitiveness
- Resale potential on platforms like Facebook Marketplace, eBay, OfferUp
- Estimated profit after fees and time investment

Only flag items as opportunities if the profit potential is significant (typically $50+)."""),
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
