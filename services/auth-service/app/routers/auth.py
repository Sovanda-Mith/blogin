from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenData,
    RefreshTokenRequest,
    APIResponse,
    PasswordChange,
)
from app.models import User
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_refresh_token_record,
    revoke_refresh_token,
    verify_refresh_token,
    get_user_by_id,
    get_password_hash,
    verify_password,
    get_user_by_email,
    decode_token,
)
from app.config import get_settings

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()

settings = get_settings()


@router.post("/register", response_model=APIResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        is_active=True,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return APIResponse(
        success=True,
        data={"user_id": str(new_user.id)},
        message="User registered successfully",
        errors=None,
    )


@router.post("/login", response_model=APIResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    refresh_token, token_id, expires_at = create_refresh_token(str(user.id))
    create_refresh_token_record(db, user.id, refresh_token, expires_at)

    return APIResponse(
        success=True,
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "is_active": user.is_active,
            },
        },
        message="Login successful",
        errors=None,
    )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)
):
    # Verify refresh token in database
    token_record = verify_refresh_token(db, refresh_data.refresh_token)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Decode and verify JWT
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    user_id = payload.get("sub")
    user = get_user_by_id(db, uuid.UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return APIResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
        message="Token refreshed successfully",
        errors=None,
    )


@router.post("/logout", response_model=APIResponse)
async def logout(
    refresh_data: RefreshTokenRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Revoke refresh token
    revoked = revoke_refresh_token(db, refresh_data.refresh_token)

    return APIResponse(
        success=True,
        data={"revoked": revoked},
        message="Logout successful",
        errors=None,
    )


@router.get("/verify", response_model=APIResponse)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return APIResponse(
        success=True,
        data={
            "user_id": payload.get("sub"),
            "exp": payload.get("exp"),
            "type": payload.get("type"),
        },
        message="Token is valid",
        errors=None,
    )


@router.get("/me", response_model=APIResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_id = payload.get("sub")
    user = get_user_by_id(db, uuid.UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return APIResponse(
        success=True,
        data={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
        },
        message="User retrieved successfully",
        errors=None,
    )


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_id = payload.get("sub")
    user = get_user_by_id(db, uuid.UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return APIResponse(
        success=True, data=None, message="Password changed successfully", errors=None
    )
