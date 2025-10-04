import hashlib
from sqlalchemy.orm import Session
from app.models import FeatureFlag

class FeatureFlagService:
    @staticmethod
    def _hash_user_flag(user_id: str, flag_name: str) -> float:
        hash_val = hashlib.sha256(f"{user_id}:{flag_name}".encode()).hexdigest()
        return int(hash_val, 16) % 100

    @staticmethod
    def evaluate_flags_for_user(db: Session, user_id: str):
        flags = db.query(FeatureFlag).all()
        user_flags = []
        for flag in flags:
            enabled = flag.status
            if enabled and flag.rollout_percentage is not None:
                hash_val = FeatureFlagService._hash_user_flag(user_id, flag.flag_name)
                enabled = hash_val < flag.rollout_percentage
            user_flags.append({
                "flag_name": flag.flag_name,
                "enabled": enabled,
                "description": flag.description
            })
        return user_flags

    @staticmethod
    def evaluate_single_flag_for_user(db: Session, flag_name: str, user_id: str):
        flag = db.query(FeatureFlag).filter(FeatureFlag.flag_name == flag_name).first()
        if not flag:
            return None
        enabled = flag.status
        if enabled and flag.rollout_percentage is not None:
            hash_val = FeatureFlagService._hash_user_flag(user_id, flag.flag_name)
            enabled = hash_val < flag.rollout_percentage
        return {
            "flag_name": flag.flag_name,
            "enabled": enabled,
            "description": flag.description
        }
