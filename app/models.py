from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, func
from app.database import Base

class FeatureFlag(Base):
    """
    SQLAlchemy model for feature flags.
    Stores configuration for feature toggles / A/B tests.
    """
    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, index=True)
    flag_name = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(Boolean, nullable=False, default=False)
    rollout_percentage = Column(Float, nullable=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
