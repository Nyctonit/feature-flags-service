import hashlib
from sqlalchemy.orm import Session
from app.models import FeatureFlag

class FeatureFlagService:
    @staticmethod
    def evaluate_flags_for_user(db: Session, user_id: str):
        """
        Evaluate all feature flags for a given user.
        Applies rollout percentage to decide if a flag is enabled.
        """
        flags = db.query(FeatureFlag).all()
        evaluated_flags = []

        for flag in flags:
            enabled = FeatureFlagService.is_flag_enabled_for_user(flag, user_id)
            evaluated_flags.append({
                "flag_name": flag.flag_name,
                "enabled": enabled,
                "description": flag.description
            })

        return evaluated_flags

    @staticmethod
    def evaluate_single_flag_for_user(db: Session, flag_name: str, user_id: str):
        """
        Evaluate a single feature flag for a user.
        Returns a dict with flag_name, enabled, description.
        """
        flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
        if not flag:
            return None

        enabled = FeatureFlagService.is_flag_enabled_for_user(flag, user_id)
        return {
            "flag_name": flag.flag_name,
            "enabled": enabled,
            "description": flag.description
        }

    @staticmethod
    def is_flag_enabled_for_user(flag: FeatureFlag, user_id: str):
        """
        Determines if a flag is enabled for a specific user.
        Uses a consistent hash for rollout percentage.
        """
        if not flag.status:
            return False  # Disabled globally

        if flag.rollout_percentage is None:
            return True  # Fully enabled

        # Hash user_id to get a consistent value between 0 and 100
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 100
        return hash_val < flag.rollout_percentage
