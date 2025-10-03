from sqlalchemy.orm import Session
from app.models import FeatureFlag
import hashlib

class FeatureFlagService:
    
    @staticmethod
    def evaluate_flags_for_user(db: Session, user_id: str):
        """
        Evaluate all feature flags for a given user.
        Applies rollout percentage logic deterministically based on user_id.
        """
        flags = db.query(FeatureFlag).all()
        user_flags = []

        for flag in flags:
            enabled = False

            if flag.status:
                if flag.rollout_percentage is None:
                    enabled = True
                else:
                    # Deterministic hash-based rollout
                    hash_value = int(hashlib.md5(f"{user_id}:{flag.flag_name}".encode()).hexdigest(), 16)
                    percentage = hash_value % 100
                    enabled = percentage < flag.rollout_percentage

            user_flags.append({
                "flag_name": flag.flag_name,
                "enabled": enabled,
                "description": flag.description
            })

        return user_flags

    @staticmethod
    def evaluate_single_flag_for_user(db: Session, flag_name: str, user_id: str):
        """
        Evaluate a single feature flag for a given user.
        Returns None if flag does not exist.
        """
        flag = db.query(FeatureFlag).filter_by(flag_name=flag_name).first()
        if not flag:
            return None

        enabled = False
        if flag.status:
            if flag.rollout_percentage is None:
                enabled = True
            else:
                hash_value = int(hashlib.md5(f"{user_id}:{flag.flag_name}".encode()).hexdigest(), 16)
                percentage = hash_value % 100
                enabled = percentage < flag.rollout_percentage

        return {
            "flag_name": flag.flag_name,
            "enabled": enabled,
            "description": flag.description
        }
