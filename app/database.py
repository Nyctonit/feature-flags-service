"""
Database configuration and connection management for Feature Flags service.
Uses SQLite for simplicity in MVP, easily switchable to PostgreSQL for production.
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - defaults to SQLite, can be overridden via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feature_flags.db")

# Create database engine
# For SQLite, we need to enable foreign key support
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL query debugging
    )
else:
    # For PostgreSQL or other databases in production
    engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models
Base = declarative_base()

def get_database_session():
    """
    Dependency function to get database session.
    Ensures proper session lifecycle management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables.
    Called during application startup.
    """
    Base.metadata.create_all(bind=engine)