from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class FeatureFlagBase(BaseModel):
    flag_name: str = Field(..., min_length=1, max_length=255)
    status: bool = Field(default=False)
    rollout_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    description: Optional[str] = None

class FeatureFlagCreate(FeatureFlagBase):
    pass

class FeatureFlagUpdate(BaseModel):
    status: Optional[bool] = None
    rollout_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    description: Optional[str] = None

class FeatureFlagResponse(FeatureFlagBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserFlagResponse(BaseModel):
    flag_name: str
    enabled: bool
    description: Optional[str] = None

class UserFlagsResponse(BaseModel):
    user_id: str
    flags: List[UserFlagResponse]

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
