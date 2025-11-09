"""
Utility functions for the Loneliness Combat Engine.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
from jose import jwt

from .config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def calculate_risk_level(score: int) -> str:
    """
    Calculate risk level based on score.

    Args:
        score: Risk score (0-100)

    Returns:
        Risk level string: low, moderate, elevated, high, critical
    """
    if score < settings.risk_score_low_threshold:
        return "low"
    elif score < settings.risk_score_moderate_threshold:
        return "moderate"
    elif score < settings.risk_score_elevated_threshold:
        return "elevated"
    elif score < 90:
        return "high"
    else:
        return "critical"


async def refresh_google_token(refresh_token: str) -> Optional[str]:
    """
    Refresh a Google OAuth access token using a refresh token.

    Args:
        refresh_token: Google OAuth refresh token

    Returns:
        New access token if successful, None otherwise
    """
    if not refresh_token:
        print("⚠️  No refresh token provided")
        return None

    # Validate that we have credentials
    if not settings.google_client_id or not settings.google_client_secret:
        print("⚠️  Google OAuth credentials not configured in backend")
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if response.status_code == 200:
                tokens = response.json()
                new_access_token = tokens.get("access_token")
                if new_access_token:
                    print("✅ Successfully refreshed Google token")
                    return new_access_token
                else:
                    print("⚠️  Token refresh response missing access_token")
                    return None
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                error_description = error_data.get("error_description", "Unknown error")
                error_code = error_data.get("error", "unknown")

                print(f"❌ Failed to refresh Google token:")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {error_code}")
                print(f"   Description: {error_description}")

                # Provide specific guidance based on error
                if "invalid_grant" in error_code:
                    print("   → Refresh token is invalid or expired. User needs to reconnect calendar.")
                elif "unauthorized_client" in error_code:
                    print("   → Client credentials mismatch. Check GOOGLE_CLIENT_ID/SECRET.")

                return None

    except httpx.TimeoutException:
        print("❌ Token refresh timed out - Google OAuth server not responding")
        return None
    except Exception as e:
        print(f"❌ Unexpected error refreshing Google token: {type(e).__name__}: {str(e)}")
        return None


async def revoke_google_token(access_token: str) -> bool:
    """
    Revoke a Google OAuth access token.

    Args:
        access_token: Google OAuth access token to revoke

    Returns:
        True if revocation successful, False otherwise
    """
    if not access_token:
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/revoke",
                params={"token": access_token},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            # Google returns 200 for successful revocation
            if response.status_code == 200:
                return True
            else:
                print(f"Failed to revoke Google token: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"Error revoking Google token: {str(e)}")
        return False
