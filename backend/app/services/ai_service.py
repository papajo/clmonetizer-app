import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-dummy") or api_key == "":
            self.llm = None
            self.api_key_configured = False
        else:
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, api_key=api_key)
            self.api_key_configured = True

    async def analyze_arbitrage(self, listing_data: dict) -> AnalysisResult:
        """
        Analyzes a listing to determine if it's a good arbitrage opportunity.
        """
        # Check if API key is configured
        if not self.api_key_configured or self.llm is None:
            return AnalysisResult(
                is_arbitrage_opportunity=False,
                profit_potential=0,
                reasoning="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable. Get your key at https://platform.openai.com/account/api-keys",
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
            if "401" in error_msg or "invalid_api_key" in error_msg.lower():
                error_msg = "Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable."
            elif "429" in error_msg or "rate_limit" in error_msg.lower():
                error_msg = "OpenAI API rate limit exceeded. Please try again later."
            else:
                error_msg = f"AI analysis error: {error_msg}"
            
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
