"""
Database models for Feature Flags service.
Defines the FeatureFlag table schema and relationships.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base

class FeatureFlag(Base):
    """
    Feature Flag model representing a single feature flag configuration.
    
    Attributes:
        id: Primary key
        flag_name: Unique name identifier for the flag
        status: Boolean indicating if flag is active (on/off)
        rollout_percentage: Optional percentage (0-100) for gradual rollout
        description: Optional description of the flag's purpose
        created_at: Timestamp when flag was created
        updated_at: Timestamp when flag was last updated
    """
    __tablename__ = "feature_flags"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Flag identifier - must be unique across all flags
    flag_name = Column(String(255), unique=True, index=True, nullable=False)
    
    # Flag status - True = enabled, False = disabled
    status = Column(Boolean, default=False, nullable=False)
    
    # Rollout percentage for gradual deployment (0-100)
    # None means flag applies to all users when status=True
    rollout_percentage = Column(Float, nullable=True)
    
    # Optional description for documentation purposes
    description = Column(String(500), nullable=True)
    
    # Timestamps for audit trail
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Database indexes for performance
    __table_args__ = (
        Index('idx_flag_name_status', 'flag_name', 'status'),
        Index('idx_status_rollout', 'status', 'rollout_percentage'),
    )

    def __repr__(self):
        return f"<FeatureFlag(flag_name='{self.flag_name}', status={self.status}, rollout={self.rollout_percentage})>"
    
    def to_dict(self):
        """Convert model instance to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "flag_name": self.flag_name,
            "status": self.status,
            "rollout_percentage": self.rollout_percentage,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }