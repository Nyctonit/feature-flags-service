"""
Feature flag evaluation service with rollout percentage logic.
Handles the business logic for determining flag states for users.
"""

import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import FeatureFlag

class FeatureFlagService:
    """
    Service class for feature flag evaluation and management.
    Handles rollout percentage logic using consistent user hashing.
    """

    @staticmethod
    def hash_user_flag(user_id: str, flag_name: str) -> float:
        """
        Generate a consistent hash value between 0-100 for a user-flag combination.
        
        This ensures:
        1. Same user always gets the same result for a flag
        2. Different users get distributed results across the percentage range
        3. Different flags for the same user can have different results
        
        Args:
            user_id: Unique identifier for the user
            flag_name: Name of the feature flag
            
        Returns:
            Float between 0 and 100 representing the user's position in the rollout
        """
        # Create a combined string for hashing
        combined = f"{user_id}:{flag_name}"
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(combined.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # Convert first 8 hex characters to integer and normalize to 0-100
        # Using first 8 chars gives us 32 bits of precision
        hash_int = int(hash_hex[:8], 16)
        hash_percentage = (hash_int / 0xFFFFFFFF) * 100
        
        return hash_percentage

    @staticmethod
    def is_flag_enabled_for_user(flag: FeatureFlag, user_id: str) -> bool:
        """
        Determine if a feature flag is enabled for a specific user.
        
        Logic:
        1. If flag status is False, always return False
        2. If flag status is True and no rollout_percentage, return True
        3. If flag status is True with rollout_percentage, use hash to determine
        
        Args:
            flag: FeatureFlag database object
            user_id: Unique identifier for the user
            
        Returns:
            Boolean indicating if flag is enabled for this user
        """
        # If flag is disabled, it's off for everyone
        if not flag.status:
            return False
        
        # If no rollout percentage specified, flag applies to all users
        if flag.rollout_percentage is None:
            return True
        
        # Calculate user's position in the rollout
        user_hash_percentage = FeatureFlagService.hash_user_flag(user_id, flag.flag_name)
        
        # User is included if their hash is within the rollout percentage
        return user_hash_percentage <= flag.rollout_percentage

    @staticmethod
    def evaluate_flags_for_user(db: Session, user_id: str) -> List[dict]:
        """
        Evaluate all feature flags for a specific user.
        
        Args:
            db: Database session
            user_id: Unique identifier for the user
            
        Returns:
            List of dictionaries containing flag evaluations
        """
        # Get all flags from database
        flags = db.query(FeatureFlag).all()
        
        # Evaluate each flag for the user
        user_flags = []
        for flag in flags:
            enabled = FeatureFlagService.is_flag_enabled_for_user(flag, user_id)
            user_flags.append({
                "flag_name": flag.flag_name,
                "enabled": enabled,
                "description": flag.description
            })
        
        return user_flags

    @staticmethod
    def evaluate_single_flag_for_user(db: Session, flag_name: str, user_id: str) -> Optional[dict]:
        """
        Evaluate a specific feature flag for a user.
        
        Args:
            db: Database session
            flag_name: Name of the feature flag
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary with flag evaluation or None if flag doesn't exist
        """
        # Get the specific flag
        flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
        
        if not flag:
            return None
        
        # Evaluate flag for user
        enabled = FeatureFlagService.is_flag_enabled_for_user(flag, user_id)
        
        return {
            "flag_name": flag.flag_name,
            "enabled": enabled,
            "description": flag.description
        }