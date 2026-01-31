from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import UserProfile
from app.schemas import UserProfileCreate, UserProfileUpdate
import uuid


def get_profile_by_user_id(db: Session, user_id: uuid.UUID) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def get_profile_by_username(db: Session, username: str) -> Optional[UserProfile]:
    return (
        db.query(UserProfile)
        .filter(func.lower(UserProfile.username) == func.lower(username))
        .first()
    )


def create_profile(
    db: Session, user_id: uuid.UUID, profile_data: UserProfileCreate
) -> UserProfile:
    profile = UserProfile(
        user_id=user_id,
        username=profile_data.username,
        display_name=profile_data.display_name,
        bio=profile_data.bio,
        avatar_url=profile_data.avatar_url,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(
    db: Session, user_id: uuid.UUID, profile_data: UserProfileUpdate
) -> Optional[UserProfile]:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return None

    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def delete_profile(db: Session, user_id: uuid.UUID) -> bool:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        return False

    db.delete(profile)
    db.commit()
    return True


def search_profiles(db: Session, query: str, skip: int = 0, limit: int = 20):
    search = f"%{query}%"
    profiles = (
        db.query(UserProfile)
        .filter(
            (UserProfile.username.ilike(search))
            | (UserProfile.display_name.ilike(search))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = (
        db.query(UserProfile)
        .filter(
            (UserProfile.username.ilike(search))
            | (UserProfile.display_name.ilike(search))
        )
        .count()
    )

    return profiles, total


def get_all_profiles(db: Session, skip: int = 0, limit: int = 20):
    profiles = db.query(UserProfile).offset(skip).limit(limit).all()
    total = db.query(UserProfile).count()
    return profiles, total


def username_exists(
    db: Session, username: str, exclude_user_id: Optional[uuid.UUID] = None
) -> bool:
    query = db.query(UserProfile).filter(
        func.lower(UserProfile.username) == func.lower(username)
    )
    if exclude_user_id:
        query = query.filter(UserProfile.user_id != exclude_user_id)
    return query.first() is not None
