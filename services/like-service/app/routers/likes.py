from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid
from jose import jwt, JWTError

from app.database import get_db
from app.schemas import LikeCreate, APIResponse, LikeCountResponse, LikeStatusResponse
from app.services.like_service import (
    create_like,
    delete_like,
    get_like_count,
    has_user_liked,
    get_post_id_by_slug,
)
from app.config import get_settings

router = APIRouter(tags=["Likes"])
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


@router.post("/", response_model=APIResponse)
async def like_post(
    like_data: LikeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Like a post (requires authentication)"""
    token = credentials.credentials
    user_id = get_current_user_id(token)

    # Look up post ID from slug
    post_id = get_post_id_by_slug(db, like_data.post_slug)
    if not post_id:
        raise HTTPException(status_code=404, detail="Post not found")

    like = create_like(db, user_id, post_id)
    if not like:
        raise HTTPException(status_code=409, detail="You have already liked this post")

    return APIResponse(
        success=True,
        data={
            "id": str(like.id),
            "post_id": str(like.post_id),
            "post_slug": like_data.post_slug,
            "user_id": str(like.user_id),
            "created_at": like.created_at.isoformat(),
        },
        message="Post liked successfully",
        errors=None,
    )


@router.delete("/{post_slug}", response_model=APIResponse)
async def unlike_post(
    post_slug: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Unlike a post (requires authentication)"""
    token = credentials.credentials
    user_id = get_current_user_id(token)

    # Look up post ID from slug
    post_id = get_post_id_by_slug(db, post_slug)
    if not post_id:
        raise HTTPException(status_code=404, detail="Post not found")

    deleted = delete_like(db, user_id, post_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Like not found or you don't have permission"
        )

    return APIResponse(
        success=True,
        data=None,
        message="Post unliked successfully",
        errors=None,
    )


@router.get("/count", response_model=APIResponse)
async def get_likes_count(
    post_slug: str = Query(..., description="Post slug to get likes count for"),
    db: Session = Depends(get_db),
):
    """Get total likes count for a post (public)"""
    # Look up post ID from slug
    post_id = get_post_id_by_slug(db, post_slug)
    if not post_id:
        raise HTTPException(status_code=404, detail="Post not found")

    count = get_like_count(db, post_id)

    return APIResponse(
        success=True,
        data={
            "post_slug": post_slug,
            "count": count,
        },
        message="Like count retrieved successfully",
        errors=None,
    )


@router.get("/status", response_model=APIResponse)
async def check_like_status(
    post_slug: str = Query(..., description="Post slug to check like status for"),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Check if current user has liked a post (requires authentication)"""
    token = credentials.credentials
    user_id = get_current_user_id(token)

    # Look up post ID from slug
    post_id = get_post_id_by_slug(db, post_slug)
    if not post_id:
        raise HTTPException(status_code=404, detail="Post not found")

    liked = has_user_liked(db, user_id, post_id)

    return APIResponse(
        success=True,
        data={
            "post_slug": post_slug,
            "liked": liked,
        },
        message="Like status retrieved successfully",
        errors=None,
    )
