"""
Authentication and authorization for FastAPI.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.core import create_access_token, decode_access_token, get_settings
from backend.models import User, get_db

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User object or None

    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user (required).

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object

    Raises:
        HTTPException: If user is not authenticated
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user


async def get_current_user_optional(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current user or create a demo user for testing.

    This allows the chat endpoint to work without authentication
    during development/demos.

    Args:
        current_user: User from get_current_user dependency
        db: Database session

    Returns:
        User object (authenticated or demo user)
    """
    if current_user:
        return current_user

    # Create or get demo user for unauthenticated requests
    demo_email = "demo@lce.local"
    demo_user = db.query(User).filter(User.email == demo_email).first()

    if not demo_user:
        demo_user = User(
            email=demo_email,
            name="Demo User",
            google_id="demo_user_id",
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    return demo_user


def create_user_token(user: User) -> str:
    """
    Create access token for user.

    Args:
        user: User object

    Returns:
        JWT access token
    """
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}, expires_delta=access_token_expires
    )

    return access_token
