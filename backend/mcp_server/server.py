"""
MCP Server for Loneliness Combat Engine.

This server exposes tools for detecting social isolation and generating interventions
through the Model Context Protocol (MCP).
"""

import json
import sys
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from backend.agents import run_detection, run_intervention
from backend.core import get_settings
from backend.models import get_db, User, Baseline, Permission

settings = get_settings()

# Create MCP server
mcp_server = FastMCP("loneliness-combat-engine")


@mcp_server.tool()
async def assess_loneliness_risk(
    user_id: str,
    user_message: str = "",
) -> str:
    """
    Comprehensive loneliness risk assessment combining multiple behavioral signals.

    Args:
        user_id: User identifier
        user_message: User's current message/concern (optional)

    Returns:
        Intervention message with risk assessment and personalized recommendations
    """
    db = next(get_db())

    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return json.dumps({"error": "User not found"})

        # Get permissions
        permission = db.query(Permission).filter(Permission.user_id == user_id).first()
        if not permission:
            return json.dumps({"error": "User permissions not set"})

        # Get baseline
        baseline = db.query(Baseline).filter(Baseline.user_id == user_id).first()

        # Default baseline values
        baseline_social_freq = 2.0
        baseline_valence = 0.5
        baseline_energy = 0.5

        if baseline and baseline.is_established == "true":
            baseline_social_freq = baseline.social_event_frequency or 2.0
            mood_baseline = baseline.mood_baseline or {}
            baseline_valence = mood_baseline.get("valence", 0.5)
            baseline_energy = mood_baseline.get("energy", 0.5)

        # Get tokens - use decryption methods
        calendar_token = None
        spotify_token = None

        if permission.calendar_enabled == "true":
            calendar_token = permission.get_google_token()

        if permission.spotify_enabled == "true":
            spotify_token = permission.get_spotify_token()

        # Run detection
        risk_assessment = await run_detection(
            user_id=user_id,
            calendar_token=calendar_token,
            spotify_token=spotify_token,
            baseline_social_frequency=baseline_social_freq,
            baseline_valence=baseline_valence,
            baseline_energy=baseline_energy,
        )

        # Run intervention
        intervention = await run_intervention(
            risk_assessment=risk_assessment,
            user_interests=None,
            user_location=None,
        )

        # Combine results
        result = {
            "risk_assessment": risk_assessment,
            "intervention": intervention,
            "user_message": user_message,
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()


@mcp_server.tool()
async def analyze_loneliness_risk(
    user_id: str,
    calendar_enabled: bool = False,
    spotify_enabled: bool = False,
) -> Dict[str, Any]:
    """
    Analyze user's loneliness risk based on behavioral patterns.

    Args:
        user_id: User identifier
        calendar_enabled: Whether to analyze Google Calendar data
        spotify_enabled: Whether to analyze Spotify data

    Returns:
        Risk assessment with score, level, and contributing factors
    """
    db = next(get_db())

    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        # Get permissions
        permission = db.query(Permission).filter(Permission.user_id == user_id).first()
        if not permission:
            return {"error": "User permissions not set"}

        # Get baseline
        baseline = db.query(Baseline).filter(Baseline.user_id == user_id).first()

        # Default baseline values
        baseline_social_freq = 2.0
        baseline_valence = 0.5
        baseline_energy = 0.5

        if baseline and baseline.is_established == "true":
            baseline_social_freq = baseline.social_event_frequency or 2.0
            mood_baseline = baseline.mood_baseline or {}
            baseline_valence = mood_baseline.get("valence", 0.5)
            baseline_energy = mood_baseline.get("energy", 0.5)

        # Get tokens - use decryption methods
        calendar_token = None
        spotify_token = None

        if calendar_enabled and permission.calendar_enabled == "true":
            calendar_token = permission.get_google_token()

        if spotify_enabled and permission.spotify_enabled == "true":
            spotify_token = permission.get_spotify_token()

        # Run detection
        result = await run_detection(
            user_id=user_id,
            calendar_token=calendar_token,
            spotify_token=spotify_token,
            baseline_social_frequency=baseline_social_freq,
            baseline_valence=baseline_valence,
            baseline_energy=baseline_energy,
        )

        return result

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@mcp_server.tool()
async def generate_intervention(
    user_id: str,
    risk_score: int,
    risk_level: str,
    interests: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate personalized intervention based on risk assessment.

    Args:
        user_id: User identifier
        risk_score: Risk score (0-100)
        risk_level: Risk level (low, moderate, elevated, high, critical)
        interests: User's interests for event matching

    Returns:
        Intervention strategy with message, activities, and action items
    """
    try:
        risk_assessment = {
            "user_id": user_id,
            "score": risk_score,
            "level": risk_level,
        }

        result = await run_intervention(
            risk_assessment=risk_assessment,
            user_interests=interests,  # Pass None if not available
            user_location=None,  # Pass None if not available
        )

        return result

    except Exception as e:
        return {"error": str(e)}


@mcp_server.tool()
async def analyze_calendar_patterns(
    user_id: str,
    days_back: int = 30,
) -> Dict[str, Any]:
    """
    Analyze user's Google Calendar to detect social withdrawal patterns.

    Args:
        user_id: User identifier
        days_back: Number of days to analyze (default: 30)

    Returns:
        Social event frequency and withdrawal patterns
    """
    db = next(get_db())

    try:
        permission = db.query(Permission).filter(Permission.user_id == user_id).first()
        if not permission or permission.calendar_enabled != "true":
            return {"error": "Calendar access not enabled"}

        from backend.tools import CalendarTool

        calendar_tool = CalendarTool(permission.get_google_token())
        frequency = await calendar_tool.calculate_social_frequency(days_back)

        return {
            "frequency": frequency,
            "period_days": days_back,
            "events_per_week": round(frequency, 2),
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@mcp_server.tool()
async def get_social_event_frequency(
    user_id: str,
    days_back: int = 30,
) -> Dict[str, Any]:
    """
    Get user's social event frequency from Google Calendar.

    Args:
        user_id: User identifier
        days_back: Number of days to analyze

    Returns:
        Social event frequency data
    """
    # Delegate to analyze_calendar_patterns
    return await analyze_calendar_patterns(user_id, days_back)


@mcp_server.tool()
async def analyze_spotify_patterns(
    user_id: str,
    days_back: int = 30,
) -> Dict[str, Any]:
    """
    Analyze user's Spotify listening patterns to detect mood shifts and isolation behaviors.

    Args:
        user_id: User identifier
        days_back: Number of days to analyze (default: 30)

    Returns:
        Mood metrics including valence, energy, and behavioral patterns
    """
    db = next(get_db())

    try:
        permission = db.query(Permission).filter(Permission.user_id == user_id).first()
        if not permission or permission.spotify_enabled != "true":
            return {"error": "Spotify access not enabled"}

        from backend.tools import SpotifyTool

        spotify_tool = SpotifyTool(permission.get_spotify_token())
        metrics = await spotify_tool.calculate_mood_metrics(days_back)

        return metrics

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@mcp_server.tool()
async def get_mood_metrics(
    user_id: str,
    days_back: int = 14,
) -> Dict[str, Any]:
    """
    Get user's mood metrics from Spotify listening history.

    Args:
        user_id: User identifier
        days_back: Number of days to analyze

    Returns:
        Mood metrics (valence, energy, etc.)
    """
    # Delegate to analyze_spotify_patterns
    return await analyze_spotify_patterns(user_id, days_back)


@mcp_server.tool()
async def find_events(
    anxiety_level: str = "medium",
    interests: Optional[List[str]] = None,
    location: str = "College Station, TX",
) -> List[Dict[str, Any]]:
    """
    Find anxiety-appropriate events based on user preferences.

    Args:
        anxiety_level: User's anxiety level (low, medium, high)
        interests: User's interests
        location: Location to search for events

    Returns:
        List of recommended events
    """
    try:
        from backend.tools import EventMatchingTool

        event_tool = EventMatchingTool()
        events = await event_tool.recommend_events(
            location=location,
            anxiety_level=anxiety_level,
            interests=interests or [],
            limit=10,
        )

        return events

    except Exception as e:
        return [{"error": str(e)}]


@mcp_server.resource("user://baselines/{user_id}")
async def get_user_baseline(user_id: str) -> str:
    """
    Get user's behavioral baseline data.

    Args:
        user_id: User identifier

    Returns:
        JSON string of baseline data
    """
    db = next(get_db())

    try:
        baseline = db.query(Baseline).filter(Baseline.user_id == user_id).first()
        if not baseline:
            return json.dumps({"error": "Baseline not found"})

        return json.dumps(baseline.to_dict())

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()


@mcp_server.resource("user://permissions/{user_id}")
async def get_user_permissions(user_id: str) -> str:
    """
    Get user's data source permissions.

    Args:
        user_id: User identifier

    Returns:
        JSON string of permission data
    """
    db = next(get_db())

    try:
        permission = db.query(Permission).filter(Permission.user_id == user_id).first()
        if not permission:
            return json.dumps({"error": "Permissions not found"})

        return json.dumps(permission.to_dict())

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()
