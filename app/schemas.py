"""
Pydantic schemas for request/response validation and serialization.
Defines the data models for API endpoints.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class FeatureFlagBase(BaseModel):
    """Base schema for feature flag data."""
    flag_name: str = Field(..., min_length=1, max_length=255, description="Unique name for the feature flag")
    status: bool = Field(default=False, description="Whether the flag is enabled (True) or disabled (False)")
    rollout_percentage: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100, 
        description="Percentage of users who should receive this flag (0-100). None means all users when status=True"
    )
    description: Optional[str] = Field(default=None, max_length=500, description="Optional description of the flag")

    @validator('rollout_percentage')
    def validate_rollout_percentage(cls, v):
        """Ensure rollout percentage is within valid range or None."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('rollout_percentage must be between 0 and 100')
        return v

class FeatureFlagCreate(FeatureFlagBase):
    """Schema for creating a new feature flag."""
    pass

class FeatureFlagUpdate(BaseModel):
    """Schema for updating an existing feature flag. All fields optional."""
    status: Optional[bool] = Field(default=None, description="Whether the flag is enabled")
    rollout_percentage: Optional[float] = Field(
        default=None, 
        ge=0, 
        le=100, 
        description="Percentage of users who should receive this flag"
    )
    description: Optional[str] = Field(default=None, max_length=500, description="Flag description")

    @validator('rollout_percentage')
    def validate_rollout_percentage(cls, v):
        """Ensure rollout percentage is within valid range or None."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('rollout_percentage must be between 0 and 100')
        return v

class FeatureFlagResponse(FeatureFlagBase):
    """Schema for feature flag responses including database fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with SQLAlchemy

class UserFlagsRequest(BaseModel):
    """Schema for requesting user-specific flags."""
    user_id: str = Field(..., min_length=1, description="Unique identifier for the user")

class UserFlagResponse(BaseModel):
    """Schema for user-specific flag evaluation response."""
    flag_name: str
    enabled: bool
    description: Optional[str] = None

class UserFlagsResponse(BaseModel):
    """Schema for multiple user flags response."""
    user_id: str
    flags: list[UserFlagResponse]

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"