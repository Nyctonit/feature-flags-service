"""
Pydantic schemas for request/response validation and serialization.
Defines the data models for API endpoints.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

# ------------------------
# Feature Flag Schemas
# ------------------------

class FeatureFlagBase(BaseModel):
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
        if v is not None and (v < 0 or v > 100):
            raise ValueError('rollout_percentage must be between 0 and 100')
        return v

class FeatureFlagCreate(FeatureFlagBase):
    pass

class FeatureFlagUpdate(BaseModel):
    status: Optional[bool] = Field(default=None)
    rollout_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    description: Optional[str] = Field(default=None, max_length=500)

    @validator('rollout_percentage')
    def validate_rollout_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('rollout_percentage must be between 0 and 100')
        return v

class FeatureFlagResponse(FeatureFlagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = dict(from_attributes=True)  # Pydantic v2 compatibility with SQLAlchemy

# ------------------------
# User Flag Schemas
# ------------------------

class UserFlagResponse(BaseModel):
    flag_name: str
    enabled: bool
    description: Optional[str] = None

    model_config = dict(from_attributes=True)

class UserFlagsResponse(BaseModel):
    user_id: str
    flags: List[UserFlagResponse]

# ------------------------
# Health Check Schema
# ------------------------

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
