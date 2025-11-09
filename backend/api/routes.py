"""
API routes for Loneliness Combat Engine.
"""

from datetime import datetime
from typing import List, Optional
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from backend.agents import run_detection, run_intervention
from backend.api.auth import create_user_token, get_current_user_optional, get_current_user_required
from backend.core import calculate_risk_level, get_settings
from backend.models import (
    Baseline,
    Intervention,
    Permission,
    RiskAssessment,
    User,
    get_db,
)
from backend.tools import EventMatchingTool

settings = get_settings()
router = APIRouter(prefix="/api/v1")


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    risk_score: Optional[int] = None
    suggestions: List[str] = []


class PermissionUpdate(BaseModel):
    enabled: bool


class ProfileUpdate(BaseModel):
    interests: Optional[str] = None  # Comma-separated interests
    location: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    interests: Optional[str] = None
    location: Optional[str] = None
    created_at: str


# Health check
@router.get("/health")
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "loneliness-combat-engine",
    }


@router.post("/auth/sync")
async def sync_auth(
    request: dict,
    db: Session = Depends(get_db),
):
    """Sync NextAuth session with backend. Creates/updates user and returns JWT token."""
    try:
        email = request.get("email")
        name = request.get("name")
        google_id = request.get("google_id")
        google_access_token = request.get("google_access_token")
        google_refresh_token = request.get("google_refresh_token")
        spotify_access_token = request.get("spotify_access_token")

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Find or create user
        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(email=email, name=name, google_id=google_id)
            db.add(user)
            db.commit()
            db.refresh(user)

            permission = Permission(user_id=user.id, calendar_enabled="false", spotify_enabled="false")
            db.add(permission)
            db.commit()
        else:
            if name:
                user.name = name
            if google_id:
                user.google_id = google_id
            db.commit()

        # Note: We no longer auto-store OAuth tokens from NextAuth sign-in.
        # Users must explicitly connect data sources (Calendar, Spotify) via Settings page.
        # This ensures proper OAuth flow with refresh tokens and user consent.

        from backend.api.auth import create_user_token
        jwt_token = create_user_token(user)

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": user.to_dict(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth sync failed: {str(e)}")


# Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Main chat endpoint for user interactions.

    Processes user messages, runs detection and intervention agents,
    and returns personalized responses.
    """
    try:
        # Get user's permissions
        permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()
        if not permission:
            # Create default permissions
            permission = Permission(user_id=current_user.id)
            db.add(permission)
            db.commit()

        # Get baseline
        baseline = db.query(Baseline).filter(Baseline.user_id == current_user.id).first()

        # Run detection - use decryption methods
        calendar_token = (
            permission.get_google_token() if permission.calendar_enabled == "true" else None
        )
        spotify_token = (
            permission.get_spotify_token() if permission.spotify_enabled == "true" else None
        )

        baseline_social = baseline.social_event_frequency if baseline else 2.0
        baseline_mood = baseline.mood_baseline if baseline else {}

        detection_result = await run_detection(
            user_id=current_user.id,
            calendar_token=calendar_token,
            spotify_token=spotify_token,
            baseline_social_frequency=baseline_social,
            baseline_valence=baseline_mood.get("valence", 0.5),
            baseline_energy=baseline_mood.get("energy", 0.5),
        )

        risk_assessment = detection_result.get("risk_assessment", {})

        # Save risk assessment
        new_assessment = RiskAssessment(
            user_id=current_user.id,
            score=risk_assessment.get("score", 50),
            level=risk_assessment.get("level", "moderate"),
            factors=risk_assessment.get("factors", {}),
        )
        db.add(new_assessment)
        db.commit()

        # Get actual user data (real interests and location)
        user_profile = db.query(User).filter(User.id == current_user.id).first()
        user_interests = user_profile.interests.split(",") if user_profile.interests else None
        user_location = user_profile.location if user_profile.location else None

        # Run intervention with user message
        intervention_result = await run_intervention(
            risk_assessment=risk_assessment,
            user_interests=user_interests,  # Real interests from user profile
            user_location=user_location,  # Real location from user profile
            user_message=request.message,
        )

        # Save intervention
        new_intervention = Intervention(
            user_id=current_user.id,
            risk_score=risk_assessment.get("score", 50),
            suggestion=intervention_result.get("message", ""),
            event_id=None,
        )
        db.add(new_intervention)
        db.commit()

        return ChatResponse(
            response=intervention_result.get("message", ""),
            risk_score=risk_assessment.get("score"),
            suggestions=intervention_result.get("action_items", []),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User endpoints
@router.get("/user/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_required),
):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        interests=current_user.interests,
        location=current_user.location,
        created_at=current_user.created_at.isoformat(),
    )


@router.patch("/user/profile")
async def update_user_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Update user profile (interests and location)."""
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields if provided
    if profile.interests is not None:
        user.interests = profile.interests
    if profile.location is not None:
        user.location = profile.location

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "interests": user.interests,
        "location": user.location,
    }


@router.get("/user/risk-score")
async def get_risk_score(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get user's latest risk score."""
    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.user_id == current_user.id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )

    if not assessment:
        return {"score": None, "level": "unknown", "message": "No assessment available yet"}

    return {
        "score": assessment.score,
        "level": assessment.level,
        "factors": assessment.factors,
        "assessed_at": assessment.assessed_at.isoformat(),
    }


@router.get("/user/wellness-score")
async def get_wellness_score(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get user's latest wellness score (inverse of risk score).
    Wellness score: 0-100, where higher = better social health.
    """
    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.user_id == current_user.id)
        .order_by(RiskAssessment.assessed_at.desc())
        .first()
    )

    if not assessment:
        return {"score": None, "level": "unknown", "message": "No assessment available yet"}

    # Convert risk score to wellness score
    wellness_score = 100 - assessment.score

    # Map risk level to wellness level
    wellness_level_map = {
        "critical": "needs_attention",
        "high": "low",
        "elevated": "moderate",
        "moderate": "good",
        "low": "excellent",
    }
    wellness_level = wellness_level_map.get(assessment.level, "good")

    return {
        "score": wellness_score,
        "level": wellness_level,
        "factors": assessment.factors,
        "assessed_at": assessment.assessed_at.isoformat(),
    }


@router.get("/user/location-status")
async def get_location_status(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Check if user has location set."""
    user = db.query(User).filter(User.id == current_user.id).first()

    has_location = bool(user.location)

    return {
        "has_location": has_location,
        "location": user.location if has_location else None,
        "message": (
            "Location is set"
            if has_location
            else "Please set your location to get personalized event recommendations"
        ),
    }


@router.get("/user/baseline")
async def get_baseline(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get user's behavioral baseline."""
    baseline = db.query(Baseline).filter(Baseline.user_id == current_user.id).first()

    if not baseline:
        return {
            "established": False,
            "message": "Baseline not yet established. We need 14 days of data.",
        }

    return baseline.to_dict()


# Permission endpoints
@router.get("/user/permissions")
async def get_permissions(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get user's data source permissions."""
    permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()

    if not permission:
        # Create default permissions
        permission = Permission(user_id=current_user.id)
        db.add(permission)
        db.commit()

    # Get base permissions dict
    perm_dict = permission.to_dict()

    # Add token status information
    perm_dict["has_google_token"] = bool(permission.get_google_token())
    perm_dict["has_spotify_token"] = bool(permission.get_spotify_token())

    return perm_dict


@router.post("/user/permissions/calendar")
async def connect_calendar(
    request: dict,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Toggle Google Calendar integration. If enabling and no token, returns OAuth URL."""
    enabled = request.get("enabled", True)

    permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()
    if not permission:
        permission = Permission(user_id=current_user.id)
        db.add(permission)

    has_token = bool(permission.get_google_token())

    # If enabling and no token exists, initiate OAuth flow
    if enabled and not has_token:
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)

        # Build Google OAuth URL specifically for calendar
        # IMPORTANT: Include email scope so we can identify the user via userinfo endpoint
        google_calendar_oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.google_client_id}&"
            f"redirect_uri={settings.google_redirect_uri.replace('/callback', '/calendar-callback')}&"
            f"response_type=code&"
            f"scope=https://www.googleapis.com/auth/calendar.readonly%20email%20profile&"
            f"state={state}&"
            f"access_type=offline&"
            f"prompt=consent"
        )

        return {
            "success": False,
            "needs_oauth": True,
            "oauth_url": google_calendar_oauth_url,
            "message": "Redirecting to Google Calendar authorization..."
        }

    # If disabling, revoke the Google token and clear stored tokens
    if not enabled:
        from backend.core.utils import revoke_google_token

        # Try to revoke the access token with Google
        access_token = permission.get_google_token()
        if access_token:
            await revoke_google_token(access_token)

        # Clear stored tokens
        permission.google_access_token = None
        permission.google_refresh_token = None

    permission.calendar_enabled = "true" if enabled else "false"
    db.commit()

    return {
        "success": True,
        "source": "calendar",
        "enabled": enabled,
        "has_token": has_token,
        "message": "Calendar access enabled" if enabled else "Calendar access disabled and tokens revoked"
    }


@router.post("/user/permissions/spotify")
async def connect_spotify(
    request: dict,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Toggle Spotify integration. If no token exists, returns oauth_url to initiate OAuth."""
    enabled = request.get("enabled", True)

    permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()
    if not permission:
        permission = Permission(user_id=current_user.id)
        db.add(permission)

    has_token = bool(permission.get_spotify_token())

    if enabled and not has_token:
        # Need to initiate OAuth flow
        state = secrets.token_urlsafe(32)
        spotify_auth_url = (
            f"https://accounts.spotify.com/authorize?"
            f"client_id={settings.spotify_client_id}&"
            f"response_type=code&"
            f"redirect_uri={settings.spotify_redirect_uri}&"
            f"scope=user-read-email%20user-read-recently-played%20user-top-read&"
            f"state={state}"
        )
        return {
            "success": False,
            "needs_oauth": True,
            "oauth_url": spotify_auth_url,
            "message": "Redirecting to Spotify authorization..."
        }

    permission.spotify_enabled = "true" if enabled else "false"
    db.commit()

    return {
        "success": True,
        "source": "spotify",
        "enabled": enabled,
        "has_token": has_token,
        "message": "Spotify access enabled" if enabled else "Spotify access disabled"
    }


# REMOVED: Generic permission endpoint - use specific endpoints for calendar/spotify
# @router.post("/user/permissions/{source}")
# async def update_permission(
#     source: str,
#     update: PermissionUpdate,
#     current_user: User = Depends(get_current_user_required),
#     db: Session = Depends(get_db),
# ):
#     """Update permission for a specific data source."""
#     valid_sources = ["calendar", "spotify", "github", "weather", "discord"]
#
#     if source not in valid_sources:
#         raise HTTPException(
#             status_code=400, detail=f"Invalid source. Must be one of: {valid_sources}"
#         )
#
#     permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()
#
#     if not permission:
#         permission = Permission(user_id=current_user.id)
#         db.add(permission)
#
#     permission.set_permission(source, update.enabled)
#     db.commit()
#
#     return {"success": True, "source": source, "enabled": update.enabled}


# Event endpoints
@router.get("/events/recommended")
async def get_recommended_events(
    anxiety_level: Optional[str] = Query(None),
    interests: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """Get recommended events based on user preferences."""
    # Get user profile
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Use provided interests or fall back to user profile
    interests_list = None
    if interests:
        interests_list = interests.split(",")
    elif user.interests:
        interests_list = user.interests.split(",")

    if not interests_list:
        return {
            "events": [],
            "message": "Please add interests to your profile to get recommendations",
        }

    # Use user's location from profile
    location = user.location if user.location else None

    if not location:
        return {
            "events": [],
            "message": "Please add your location to your profile to get event recommendations",
        }

    event_tool = EventMatchingTool()
    events = await event_tool.recommend_events(
        location=location,
        anxiety_level=anxiety_level,
        interests=interests_list,
        limit=10,
    )

    return {"events": events}


@router.get("/interventions/history")
async def get_intervention_history(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    limit: int = Query(10, le=50),
):
    """Get user's intervention history."""
    interventions = (
        db.query(Intervention)
        .filter(Intervention.user_id == current_user.id)
        .order_by(Intervention.created_at.desc())
        .limit(limit)
        .all()
    )

    return {"interventions": [i.to_dict() for i in interventions]}


# Google OAuth endpoints
@router.get("/auth/google")
async def google_auth():
    """
    Initiate Google OAuth flow.
    Redirects user to Google's consent screen.
    """
    state = secrets.token_urlsafe(32)

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.google_redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile%20https://www.googleapis.com/auth/calendar.readonly&"
        f"state={state}&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    return RedirectResponse(url=google_auth_url)


@router.get("/auth/google/calendar-callback")
async def google_calendar_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Handle Google Calendar OAuth callback (separate from sign-in).
    Exchanges authorization code for calendar access token.
    """
    print(f"\n{'='*60}")
    print(f"🔄 CALENDAR OAUTH CALLBACK TRIGGERED")
    print(f"{'='*60}")
    print(f"  Code: {code[:20] if code else None}...")
    print(f"  State: {state}")
    print(f"  Error: {error}")
    print(f"{'='*60}\n")

    # Check for OAuth errors from Google
    if error:
        print(f"❌ Google OAuth error: {error}")
        return RedirectResponse(url=f"http://localhost:3000/settings?error=google_oauth_{error}")

    if not code:
        print(f"❌ No authorization code received")
        return RedirectResponse(url="http://localhost:3000/settings?error=no_auth_code")

    try:
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            print(f"🔄 Exchanging authorization code for access token...")
            print(f"   Redirect URI: {settings.google_redirect_uri.replace('/callback', '/calendar-callback')}")

            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri.replace('/callback', '/calendar-callback'),
                    "grant_type": "authorization_code",
                },
            )

            print(f"📡 Token exchange response status: {token_response.status_code}")

            if token_response.status_code != 200:
                error_detail = token_response.text
                print(f"❌ Token exchange failed: {error_detail}")
                return RedirectResponse(url=f"http://localhost:3000/settings?error=calendar_auth_failed")

            tokens = token_response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token")

            # Get user info from Google (to match with our user)
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                return RedirectResponse(url="http://localhost:3000/settings?error=user_info_failed")

            userinfo = userinfo_response.json()
            user_email = userinfo.get("email")

            print(f"🔐 Calendar OAuth callback for user: {user_email}")

            # Find user by email
            user = db.query(User).filter(User.email == user_email).first()

            if not user:
                print(f"❌ User not found: {user_email}")
                return RedirectResponse(url="http://localhost:3000/settings?error=user_not_found")

            # Validate access token
            if not access_token:
                print(f"❌ No access token received for user: {user_email}")
                return RedirectResponse(url="http://localhost:3000/settings?error=no_access_token")

            print(f"✅ Access token received for user: {user_email}")

            # Store Calendar token
            from backend.core.encryption import encrypt_token
            permission = db.query(Permission).filter(Permission.user_id == user.id).first()

            # Create permission record if it doesn't exist
            if not permission:
                print(f"⚠️  No permission record found, creating new one for user: {user.id}")
                permission = Permission(user_id=user.id)
                db.add(permission)
            else:
                print(f"✅ Found existing permission record for user: {user.id}")

            # Store tokens and enable calendar
            print(f"💾 Storing access token (length: {len(access_token)})...")
            permission.set_google_token(access_token)
            if refresh_token:
                permission.google_refresh_token = encrypt_token(refresh_token)
                print(f"✅ Refresh token stored (length: {len(refresh_token)})")
            permission.calendar_enabled = "true"

            print(f"💾 Committing to database...")
            db.commit()
            print(f"✅ Database commit successful")

            # Verify the data was saved
            db.refresh(permission)
            has_token = bool(permission.get_google_token())
            print(f"🔍 Verification - calendar_enabled: {permission.calendar_enabled}, has_token: {has_token}")

            print(f"✅ Calendar connected successfully for user: {user_email}")

            return RedirectResponse(url="http://localhost:3000/settings?calendar=connected")

    except Exception as e:
        import traceback
        print(f"\n❌ CALENDAR OAUTH CALLBACK ERROR:")
        print(f"   Error: {str(e)}")
        print(f"   Traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return RedirectResponse(url=f"http://localhost:3000/settings?error={str(e)}")


@router.get("/auth/google/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback (for sign-in only, not calendar access).
    Exchanges authorization code for access token and creates/updates user.
    """
    try:
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )

            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")

            tokens = token_response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token")

            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")

            userinfo = userinfo_response.json()

            # Check if user exists
            user = db.query(User).filter(User.email == userinfo["email"]).first()

            if not user:
                # Create new user (sign-in only, no calendar access)
                user = User(
                    email=userinfo["email"],
                    name=userinfo.get("name"),
                    google_id=userinfo["id"],
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                # Create default permissions (NO tokens stored during sign-in)
                permission = Permission(
                    user_id=user.id,
                    calendar_enabled="false",
                    spotify_enabled="false",
                )
                db.add(permission)
                db.commit()
            else:
                # Update existing user's basic info only (not tokens)
                if userinfo.get("name"):
                    user.name = userinfo.get("name")
                if userinfo["id"]:
                    user.google_id = userinfo["id"]
                db.commit()

            # Create JWT token
            jwt_token = create_user_token(user)

            # Redirect to frontend with token
            frontend_url = f"{settings.google_redirect_uri.rsplit('/', 1)[0]}?token={jwt_token}"
            return RedirectResponse(url=frontend_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/auth/spotify/callback")
async def spotify_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle Spotify OAuth callback and store tokens."""
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.spotify_redirect_uri,
                    "client_id": settings.spotify_client_id,
                    "client_secret": settings.spotify_client_secret,
                },
            )

            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to exchange code: {token_response.text}")

            tokens = token_response.json()
            access_token = tokens["access_token"]
            refresh_token = tokens.get("refresh_token")

            # Get user info from Spotify
            userinfo_response = await client.get(
                "https://api.spotify.com/v1/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Spotify user info")

            userinfo = userinfo_response.json()
            spotify_email = userinfo.get("email")

            # Find user by email
            user = db.query(User).filter(User.email == spotify_email).first()

            if not user:
                return RedirectResponse(url="http://localhost:3000/settings?error=user_not_found")

            # Validate access token
            if not access_token:
                return RedirectResponse(url="http://localhost:3000/settings?error=no_access_token")

            # Store Spotify token
            from backend.core.encryption import encrypt_token
            permission = db.query(Permission).filter(Permission.user_id == user.id).first()

            # Create permission record if it doesn't exist
            if not permission:
                permission = Permission(user_id=user.id)
                db.add(permission)

            # Store tokens and enable Spotify
            permission.set_spotify_token(access_token)
            if refresh_token:
                permission.spotify_refresh_token = encrypt_token(refresh_token)
            permission.spotify_enabled = "true"
            db.commit()

            return RedirectResponse(url="http://localhost:3000/settings?spotify=connected")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify auth failed: {str(e)}")


# Calendar endpoints
@router.get("/user/calendar/events")
async def get_calendar_events(
    days_back: int = Query(30, ge=1, le=365),
    days_ahead: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    """
    Get user's calendar events (past and upcoming).

    Args:
        days_back: Number of days to look back (default: 30)
        days_ahead: Number of days to look ahead (default: 7)
    """
    try:
        # Check if user has calendar enabled
        permission = db.query(Permission).filter(Permission.user_id == current_user.id).first()

        if not permission or permission.calendar_enabled != "true":
            raise HTTPException(
                status_code=403,
                detail="Calendar access not enabled. Please enable it in settings."
            )

        # Get calendar tokens
        calendar_token = permission.get_google_token()

        if not calendar_token:
            raise HTTPException(
                status_code=401,
                detail="Calendar token not found. Please reconnect your Google Calendar in settings."
            )

        # Import CalendarTool and utilities
        from backend.tools.calendar_tool import CalendarTool
        from backend.core.utils import refresh_google_token
        from backend.core.encryption import decrypt_token

        # Try to fetch events, refresh token if needed
        try:
            # Initialize calendar tool with token
            calendar_tool = CalendarTool(access_token=calendar_token)

            # Get past social events
            past_events = await calendar_tool.get_social_events(days_back=days_back)

            # Get upcoming events
            upcoming_events = await calendar_tool.get_upcoming_social_events(days_ahead=days_ahead)

            # Get comprehensive social analysis
            social_analysis = await calendar_tool.analyze_social_patterns(days_back=days_back)

        except Exception as calendar_error:
            # If calendar API fails, try to refresh the token
            print(f"⚠️  Calendar API error: {type(calendar_error).__name__}: {str(calendar_error)}")

            refresh_token = decrypt_token(permission.google_refresh_token) if permission.google_refresh_token else None

            if not refresh_token:
                print("❌ No refresh token available for calendar")
                raise HTTPException(
                    status_code=401,
                    detail="Your calendar connection has expired. Please reconnect your Google Calendar in Settings to continue."
                )

            # Attempt to refresh the token
            print("🔄 Attempting to refresh calendar access token...")
            new_access_token = await refresh_google_token(refresh_token)

            if not new_access_token:
                print("❌ Token refresh failed")
                raise HTTPException(
                    status_code=401,
                    detail="Unable to refresh your calendar access. Please disconnect and reconnect your Google Calendar in Settings."
                )

            # Update the stored access token
            print("✅ Token refreshed successfully, updating database...")
            permission.set_google_token(new_access_token)
            db.commit()

            # Retry with the new token
            print("🔄 Retrying calendar fetch with new token...")
            calendar_tool = CalendarTool(access_token=new_access_token)
            past_events = await calendar_tool.get_social_events(days_back=days_back)
            upcoming_events = await calendar_tool.get_upcoming_social_events(days_ahead=days_ahead)
            social_analysis = await calendar_tool.analyze_social_patterns(days_back=days_back)
            print("✅ Calendar data fetched successfully after token refresh")

        return {
            "past_events": past_events,
            "upcoming_events": upcoming_events,
            "analysis": social_analysis,
            "period": {
                "days_back": days_back,
                "days_ahead": days_ahead
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch calendar events: {str(e)}")
