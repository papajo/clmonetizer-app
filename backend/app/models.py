from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    price = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date_posted = Column(DateTime, nullable=True)
    date_scraped = Column(DateTime, default=datetime.utcnow)
    
    # Meta fields
    source = Column(String, default="craigslist")
    category = Column(String, nullable=True)
    
    # Attributes extracted by AI or parsing
    mileage = Column(Integer, nullable=True)
    engine_displacement = Column(String, nullable=True)
    
    # Arbitrage analysis
    analysis_json = Column(JSON, nullable=True) # Store full AI analysis
    is_arbitrage_opportunity = Column(Boolean, default=False)
    profit_potential = Column(Float, nullable=True)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    
    lead_type = Column(String, index=True) # e.g., "wanted", "service_target"
    contact_info = Column(String, nullable=True)
    status = Column(String, default="new") # new, contacted, sold
    
    created_at = Column(DateTime, default=datetime.utcnow)
