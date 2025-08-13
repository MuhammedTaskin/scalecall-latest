"""
Database models and initialization for the telco agent.
"""
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database URL - SQLite for simplicity
DATABASE_URL = "sqlite:///./telecom_agent.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """User/customer model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    msisdn = Column(String, nullable=False, unique=True)
    maiden_name = Column(String, nullable=False)
    package_id = Column(String, nullable=True)
    contract_end = Column(String, nullable=True)
    payment_status = Column(String, default="active")
    device_imei = Column(String, nullable=True)
    activation_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class Package(Base):
    """Data package model."""
    __tablename__ = "packages"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    data = Column(String, nullable=False)  # e.g., "5GB", "Unlimited"
    price = Column(Float, nullable=False)
    validity = Column(String, nullable=False)  # e.g., "30 days"
    features = Column(Text, nullable=True)  # JSON string
    country_code = Column(String, default="TR")
    active = Column(Boolean, default=True)


class Session(Base):
    """User session model."""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    transcript_json = Column(Text, nullable=True)  # JSON string
    persona_changes = Column(Text, nullable=True)  # JSON string


class ToolCall(Base):
    """Tool call logging model."""
    __tablename__ = "tool_calls"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=True)
    tool_name = Column(String, nullable=False)
    arguments_json = Column(Text, nullable=False)
    result_json = Column(Text, nullable=False)
    success = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    execution_time_ms = Column(Integer, nullable=True)


class SupportTicket(Base):
    """Support ticket model."""
    __tablename__ = "tickets"
    
    ticket_id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Memory(Base):
    """Optional user memory/preferences model."""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    tone_preference = Column(String, nullable=True)
    last_intent = Column(String, nullable=True)
    context_data = Column(Text, nullable=True)  # JSON string
    updated_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database and seed with sample data."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
        # Seed sample data
        await seed_data()
        logger.info("Database seeded with sample data")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


async def seed_data():
    """Seed database with sample users and packages."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            logger.info("Database already seeded")
            return
        
        # Sample users
        users_data = [
            {
                "id": "12345",
                "name": "Ahmet Yılmaz",
                "msisdn": "905551234567", 
                "maiden_name": "Kaya",
                "package_id": "premium_10gb",
                "contract_end": "2024-12-31",
                "payment_status": "active",
                "device_imei": "123456789012345",
                "activation_status": "active"
            },
            {
                "id": "67890",
                "name": "Fatma Demir",
                "msisdn": "905559876543",
                "maiden_name": "Özkan", 
                "package_id": "basic_5gb",
                "contract_end": "2024-11-30",
                "payment_status": "active",
                "device_imei": "987654321098765",
                "activation_status": "pending"
            }
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        # Sample packages
        packages_data = [
            {
                "id": "basic_5gb",
                "name": "Temel 5GB",
                "data": "5GB", 
                "price": 99.99,
                "validity": "30 gün",
                "features": json.dumps([
                    "5GB yüksek hız internet",
                    "Sınırsız konuşma", 
                    "1000 SMS"
                ])
            },
            {
                "id": "premium_10gb",
                "name": "Premium 10GB",
                "data": "10GB",
                "price": 149.99,
                "validity": "30 gün",
                "features": json.dumps([
                    "10GB yüksek hız internet",
                    "Sınırsız konuşma",
                    "Sınırsız SMS", 
                    "5G destekli"
                ])
            },
            {
                "id": "unlimited",
                "name": "Sınırsız",
                "data": "Sınırsız",
                "price": 299.99,
                "validity": "30 gün",
                "features": json.dumps([
                    "Sınırsız yüksek hız internet",
                    "Sınırsız konuşma",
                    "Sınırsız SMS",
                    "5G destekli",
                    "Uluslararası 100 dakika"
                ])
            }
        ]
        
        for package_data in packages_data:
            package = Package(**package_data)
            db.add(package)
        
        db.commit()
        logger.info("Sample data seeded successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding data: {e}")
    finally:
        db.close()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
