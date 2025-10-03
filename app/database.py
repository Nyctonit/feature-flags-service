from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Use SQLite for simplicity; replace with PostgreSQL or MySQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./feature_flags.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_database_session() -> Session:
    """
    Dependency function to get a database session for FastAPI endpoints.
    Usage: `db: Session = Depends(get_database_session)`
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    Should be called at application startup.
    """
    Base.metadata.create_all(bind=engine)
