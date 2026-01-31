from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import uuid

from app.database import get_db
from app.schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    APIResponse,
    PaginationParams,
    PaginatedResponse,
)
from app.models import UserProfile
from app.services.user_service import (
    get_profile_by_user_id,
    get_profile_by_username,
    create_profile,
    update_profile,
    delete_profile,
    search_profiles,
    get_all_profiles,
    username_exists,
)
from app.config import get_settings
from jose import jwt, JWTError

router = APIRouter(tags=["Users"])
security = HTTPBearer()
settings = get_settings()


def get_current_user_id(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        return uuid.UUID(user_id)
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )


@router.get("/profiles/search", response_model=APIResponse)
async def search_user_profiles(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    profiles, total = search_profiles(db, q, skip=skip, limit=limit)
    total_pages = (total + limit - 1) // limit

    return APIResponse(
        success=True,
        data={
            "items": [
                {
                    "user_id": str(p.user_id),
                    "username": p.username,
                    "display_name": p.display_name,
                    "bio": p.bio,
                    "avatar_url": p.avatar_url,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in profiles
            ],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        message="Profiles retrieved successfully",
        errors=None,
    )


@router.get("/profiles", response_model=APIResponse)
async def list_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    profiles, total = get_all_profiles(db, skip=skip, limit=limit)
    total_pages = (total + limit - 1) // limit

    return APIResponse(
        success=True,
        data={
            "items": [
                {
                    "user_id": str(p.user_id),
                    "username": p.username,
                    "display_name": p.display_name,
                    "bio": p.bio,
                    "avatar_url": p.avatar_url,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat(),
                }
                for p in profiles
            ],
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        },
        message="Profiles retrieved successfully",
        errors=None,
    )


@router.get("/profiles/{username}", response_model=APIResponse)
async def get_profile_by_username_endpoint(
    username: str, db: Session = Depends(get_db)
):
    profile = get_profile_by_username(db, username)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return APIResponse(
        success=True,
        data={
            "user_id": str(profile.user_id),
            "username": profile.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        },
        message="Profile retrieved successfully",
        errors=None,
    )


@router.post("/profiles", response_model=APIResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    user_id = get_current_user_id(token)

    # Check if profile already exists
    existing_profile = get_profile_by_user_id(db, user_id)
    if existing_profile:
        raise HTTPException(
            status_code=400, detail="Profile already exists for this user"
        )

    # Check if username is taken
    if username_exists(db, profile_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    profile = create_profile(db, user_id, profile_data)

    return APIResponse(
        success=True,
        data={
            "user_id": str(profile.user_id),
            "username": profile.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        },
        message="Profile created successfully",
        errors=None,
    )


@router.put("/profiles/me", response_model=APIResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    user_id = get_current_user_id(token)

    profile = update_profile(db, user_id, profile_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return APIResponse(
        success=True,
        data={
            "user_id": str(profile.user_id),
            "username": profile.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        },
        message="Profile updated successfully",
        errors=None,
    )


@router.delete("/profiles/me", response_model=APIResponse)
async def delete_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    user_id = get_current_user_id(token)

    deleted = delete_profile(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")

    return APIResponse(
        success=True, data=None, message="Profile deleted successfully", errors=None
    )


@router.get("/me", response_model=APIResponse)
async def get_my_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    user_id = get_current_user_id(token)

    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return APIResponse(
        success=True,
        data={
            "user_id": str(profile.user_id),
            "username": profile.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            "avatar_url": profile.avatar_url,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        },
        message="Profile retrieved successfully",
        errors=None,
    )
