"""
Main FastAPI application for Feature Flags / A/B Testing microservice.
Provides REST API endpoints for managing and evaluating feature flags.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import List

# Import our application modules
from app.database import get_database_session, create_tables
from app.models import FeatureFlag
from app.schemas import (
    FeatureFlagCreate, 
    FeatureFlagUpdate, 
    FeatureFlagResponse,
    UserFlagsResponse,
    UserFlagResponse,
    HealthResponse
)
from app.feature_flag_service import FeatureFlagService

# Create FastAPI application instance
app = FastAPI(
    title="Feature Flags Service",
    description="A minimal Feature Flags / A/B Testing microservice MVP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Root route
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Feature Flags Service is running 🚀", "docs": "/docs"}

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    create_tables()
    print("Feature Flags Service started successfully!")

# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and deployment verification.
    Returns service status and metadata.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

# Feature Flag Management Endpoints

@app.post("/flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED, tags=["Flags"])
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new feature flag.
    
    - **flag_name**: Unique name for the feature flag
    - **status**: Whether the flag is enabled (true) or disabled (false)
    - **rollout_percentage**: Optional percentage (0-100) for gradual rollout
    - **description**: Optional description of the flag's purpose
    """
    try:
        # Create new flag instance
        db_flag = FeatureFlag(
            flag_name=flag_data.flag_name,
            status=flag_data.status,
            rollout_percentage=flag_data.rollout_percentage,
            description=flag_data.description
        )
        
        # Add to database
        db.add(db_flag)
        db.commit()
        db.refresh(db_flag)
        
        return db_flag
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature flag with name '{flag_data.flag_name}' already exists"
        )

@app.get("/flags", response_model=List[FeatureFlagResponse], tags=["Flags"])
async def list_feature_flags(db: Session = Depends(get_database_session)):
    """
    Retrieve all feature flags in the system.
    Returns the raw flag configurations without user-specific evaluation.
    """
    flags = db.query(FeatureFlag).all()
    return flags

@app.get("/flags/{flag_name}", response_model=FeatureFlagResponse, tags=["Flags"])
async def get_feature_flag(
    flag_name: str,
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a specific feature flag by name.
    Returns the raw flag configuration without user-specific evaluation.
    """
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    return flag

@app.put("/flags/{flag_name}", response_model=FeatureFlagResponse, tags=["Flags"])
async def update_feature_flag(
    flag_name: str,
    flag_update: FeatureFlagUpdate,
    db: Session = Depends(get_database_session)
):
    """
    Update an existing feature flag.
    Only provided fields will be updated; others remain unchanged.
    """
    # Find the existing flag
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    # Update provided fields
    update_data = flag_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flag, field, value)
    
    # Save changes
    db.commit()
    db.refresh(flag)
    
    return flag

@app.delete("/flags/{flag_name}", status_code=status.HTTP_204_NO_CONTENT, tags=["Flags"])
async def delete_feature_flag(
    flag_name: str,
    db: Session = Depends(get_database_session)
):
    """
    Delete a feature flag.
    This will permanently remove the flag from the system.
    """
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    db.delete(flag)
    db.commit()
    
    return None

# User-specific Flag Evaluation Endpoints

@app.get("/users/{user_id}/flags", response_model=UserFlagsResponse, tags=["User Flags"])
async def get_user_flags(
    user_id: str,
    db: Session = Depends(get_database_session)
):
    """
    Get all feature flags evaluated for a specific user.
    Applies rollout percentage logic to determine which flags are enabled.
    
    - **user_id**: Unique identifier for the user
    """
    # Evaluate all flags for the user
    user_flags = FeatureFlagService.evaluate_flags_for_user(db, user_id)
    
    return UserFlagsResponse(
        user_id=user_id,
        flags=[UserFlagResponse(**flag) for flag in user_flags]
    )

@app.get("/users/{user_id}/flags/{flag_name}", response_model=UserFlagResponse, tags=["User Flags"])
async def get_user_flag(
    user_id: str,
    flag_name: str,
    db: Session = Depends(get_database_session)
):
    """
    Get a specific feature flag evaluated for a user.
    Applies rollout percentage logic to determine if the flag is enabled.
    
    - **user_id**: Unique identifier for the user
    - **flag_name**: Name of the feature flag to evaluate
    """
    # Evaluate the specific flag for the user
    result = FeatureFlagService.evaluate_single_flag_for_user(db, flag_name, user_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    return UserFlagResponse(**result)

# Error handling
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors with appropriate HTTP status."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
