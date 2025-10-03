from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ------------------------
# Database setup
# ------------------------

DATABASE_URL = "sqlite:///./feature_flags.db"  # Local SQLite file

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Required for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------
# Dependency for FastAPI
# ------------------------

def get_database_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# Table creation
# ------------------------

def create_tables():
    """Create all tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
