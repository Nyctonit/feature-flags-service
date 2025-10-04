"""
Main FastAPI application for Feature Flags / A/B Testing microservice.
"""

import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Import app modules
from app.database import get_database_session, create_tables
from app.models import FeatureFlag
from app.schemas import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    UserFlagsResponse,
    UserFlagResponse,
    HealthResponse,
)
from app.feature_flag_service import FeatureFlagService

# App instance
app = FastAPI(
    title="Feature Flags Service",
    description="A minimal Feature Flags / A/B Testing microservice MVP",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize DB tables on startup"""
    create_tables()
    print("🚀 Feature Flags Service started successfully!")


# Health check
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


# === Feature Flag Management ===
@app.post("/flags", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED, tags=["Flags"])
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    db: Session = Depends(get_database_session)
):
    try:
        db_flag = FeatureFlag(
            flag_name=flag_data.flag_name,
            status=flag_data.status,
            rollout_percentage=flag_data.rollout_percentage,
            description=flag_data.description
        )
        db.add(db_flag)
        db.commit()
        db.refresh(db_flag)
        return db_flag
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature flag '{flag_data.flag_name}' already exists"
        )


@app.get("/flags", response_model=List[FeatureFlagResponse], tags=["Flags"])
async def list_feature_flags(db: Session = Depends(get_database_session)):
    return db.query(FeatureFlag).all()


@app.get("/flags/{flag_name}", response_model=FeatureFlagResponse, tags=["Flags"])
async def get_feature_flag(flag_name: str, db: Session = Depends(get_database_session)):
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")
    return flag


@app.put("/flags/{flag_name}", response_model=FeatureFlagResponse, tags=["Flags"])
async def update_feature_flag(
    flag_name: str,
    flag_update: FeatureFlagUpdate,
    db: Session = Depends(get_database_session)
):
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")

    for field, value in flag_update.dict(exclude_unset=True).items():
        setattr(flag, field, value)

    db.commit()
    db.refresh(flag)
    return flag


@app.delete("/flags/{flag_name}", status_code=204, tags=["Flags"])
async def delete_feature_flag(flag_name: str, db: Session = Depends(get_database_session)):
    flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
    if not flag:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")

    db.delete(flag)
    db.commit()
    return None


# === User Flag Evaluation ===
@app.get("/users/{user_id}/flags", response_model=UserFlagsResponse, tags=["User Flags"])
async def get_user_flags(user_id: str, db: Session = Depends(get_database_session)):
    user_flags = FeatureFlagService.evaluate_flags_for_user(db, user_id)
    return UserFlagsResponse(
        user_id=user_id,
        flags=[UserFlagResponse(**flag) for flag in user_flags]
    )


@app.get("/users/{user_id}/flags/{flag_name}", response_model=UserFlagResponse, tags=["User Flags"])
async def get_user_flag(user_id: str, flag_name: str, db: Session = Depends(get_database_session)):
    result = FeatureFlagService.evaluate_single_flag_for_user(db, flag_name, user_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' not found")
    return UserFlagResponse(**result)


# Error handler
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Local run (not used in Render since gunicorn runs it)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
