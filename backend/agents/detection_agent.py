"""
Detection Agent for Loneliness Combat Engine.

This module analyzes user behavioral data from multiple sources
(Google Calendar, Spotify) to calculate loneliness risk scores.

Key Functions:
    - run_detection(): Main entry point, coordinates all analysis
    - analyze_social_patterns(): Analyzes calendar events
    - analyze_mood_patterns(): Analyzes Spotify listening
    - calculate_loneliness_risk_score(): Combines metrics into risk score

Data Sources:
    - Google Calendar: Social event frequency, declined invitations
    - Spotify: Mood via audio features, late-night listening patterns

Risk Scoring:
    - 0-24: Low risk (healthy social connections)
    - 25-49: Moderate risk (some decline in social activity)
    - 50-74: Elevated risk (significant isolation patterns)
    - 75-100: High/Critical risk (severe isolation, intervention needed)
"""

from typing import Any, Dict, Optional

from backend.core import get_settings
from backend.models.risk_assessment import RiskCalculator
from backend.tools import CalendarTool, SpotifyTool

settings = get_settings()


async def analyze_social_patterns(
    user_id: str,
    calendar_token: Optional[str] = None,
    baseline_frequency: float = 2.0,
) -> Dict[str, Any]:
    """
    Analyze social event patterns from Google Calendar.

    Args:
        user_id: User identifier
        calendar_token: Google OAuth token for calendar access
        baseline_frequency: User's baseline social event frequency (events/week)

    Returns:
        Dictionary with social pattern analysis and risk contribution
    """
    if not calendar_token:
        return {
            "available": False,
            "risk_contribution": 0,
            "message": "Calendar access not granted",
        }

    try:
        calendar_tool = CalendarTool(calendar_token)
        decline_analysis = await calendar_tool.detect_social_decline(
            baseline_frequency=baseline_frequency, current_period_days=14
        )

        # Calculate risk contribution (0-40 points)
        decline_percentage = decline_analysis.get("decline_percentage", 0)
        risk_contribution = min(40, int(decline_percentage * 0.8))  # Max 40 points

        return {
            "available": True,
            "baseline_frequency": baseline_frequency,
            "current_frequency": decline_analysis.get("current_frequency"),
            "decline_percentage": decline_percentage,
            "is_declining": decline_analysis.get("is_declining"),
            "risk_contribution": risk_contribution,
        }

    except Exception as e:
        print(f"Error analyzing social patterns: {e}")
        return {"available": False, "risk_contribution": 0, "error": str(e)}


async def analyze_mood_patterns(
    user_id: str,
    spotify_token: Optional[str] = None,
    baseline_valence: float = 0.5,
    baseline_energy: float = 0.5,
) -> Dict[str, Any]:
    """
    Analyze mood patterns from Spotify listening history.

    Args:
        user_id: User identifier
        spotify_token: Spotify OAuth token
        baseline_valence: User's baseline valence (positivity)
        baseline_energy: User's baseline energy level

    Returns:
        Dictionary with mood analysis and risk contribution
    """
    if not spotify_token:
        return {
            "available": False,
            "risk_contribution": 0,
            "message": "Spotify access not granted",
        }

    try:
        spotify_tool = SpotifyTool(spotify_token)

        # Detect mood shift
        baseline_metrics = {"valence": baseline_valence, "energy": baseline_energy}
        mood_shift = await spotify_tool.detect_mood_shift(
            baseline_metrics=baseline_metrics, current_period_days=7
        )

        # Detect late-night listening
        late_night_analysis = await spotify_tool.detect_late_night_listening(days_back=7)

        # Calculate risk contribution (0-35 points)
        risk_contribution = 0

        if mood_shift.get("shift_detected"):
            valence_change = abs(mood_shift.get("valence_change", 0))
            risk_contribution += min(20, int(valence_change * 100))

        if late_night_analysis.get("is_concerning"):
            late_night_pct = late_night_analysis.get("late_night_percentage", 0)
            risk_contribution += min(15, int(late_night_pct * 0.3))

        risk_contribution = min(35, risk_contribution)  # Cap at 35 points

        return {
            "available": True,
            "mood_shift": mood_shift,
            "late_night_analysis": late_night_analysis,
            "risk_contribution": risk_contribution,
        }

    except Exception as e:
        print(f"Error analyzing mood patterns: {e}")
        return {"available": False, "risk_contribution": 0, "error": str(e)}


async def calculate_loneliness_risk_score(
    user_id: str,
    spotify_metrics: Dict[str, Any],
    calendar_metrics: Dict[str, Any],
    baseline_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate overall loneliness risk score (0-100) using RiskCalculator.

    Args:
        user_id: User identifier
        spotify_metrics: Spotify listening pattern metrics
        calendar_metrics: Calendar social event metrics
        baseline_data: User's baseline behavioral data (optional)

    Returns:
        Dictionary with risk score, level, factors, and explanation
    """
    # Use RiskCalculator to compute risk score
    risk_result = RiskCalculator.calculate_risk(
        spotify_metrics=spotify_metrics,
        calendar_metrics=calendar_metrics,
        baseline_data=baseline_data,
    )

    # Add user_id and timestamp for database storage
    return {
        "user_id": user_id,
        "score": risk_result["score"],
        "level": risk_result["level"],
        "factors": risk_result["factors"],
        "explanation": risk_result["explanation"],
        "timestamp": None,  # Will be set by database
    }


async def run_detection(
    user_id: str,
    calendar_token: Optional[str] = None,
    spotify_token: Optional[str] = None,
    baseline_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run the detection pipeline to assess loneliness risk.

    Simplified version without Google ADK - directly calls tools and RiskCalculator.

    Args:
        user_id: User identifier
        calendar_token: Google Calendar OAuth token
        spotify_token: Spotify OAuth token
        baseline_data: User's baseline behavioral data (optional)

    Returns:
        Risk assessment dictionary with:
        - risk_assessment: Overall risk score and explanation
        - spotify_metrics: Raw Spotify analysis data
        - calendar_metrics: Raw Calendar analysis data
    """
    # Initialize metrics dictionaries
    spotify_metrics = {}
    calendar_metrics = {}

    # Analyze Spotify patterns if token provided
    if spotify_token:
        try:
            spotify_tool = SpotifyTool(spotify_token)

            # Get recent tracks and calculate metrics
            recent_tracks = await spotify_tool.get_recent_tracks(limit=50)

            # Calculate mood metrics
            mood_data = await spotify_tool.calculate_enhanced_mood_metrics(days_back=30)

            # Detect late-night listening
            late_night_data = await spotify_tool.detect_late_night_listening(days_back=30)

            # Build spotify metrics for RiskCalculator
            baseline_valence = (
                baseline_data.get("mood_baseline", {}).get("valence", 0.5) if baseline_data else 0.5
            )
            baseline_listening_hours = (
                baseline_data.get("music_patterns", {}).get("daily_hours", 3) * 30
                if baseline_data
                else 90
            )  # 3h/day * 30 days

            spotify_metrics = {
                "baseline_listening_hours": baseline_listening_hours,
                "current_listening_hours": mood_data.get("total_listening_hours", 90),
                "late_night_percentage": late_night_data.get("late_night_percentage", 0),
                "baseline_valence": baseline_valence,
                "current_valence": mood_data.get("valence", 0.5),
                "repeat_listening_percentage": mood_data.get("repeat_percentage", 0),
            }

        except Exception as e:
            print(f"Error analyzing Spotify patterns: {e}")
            # Use defaults on error
            spotify_metrics = {
                "baseline_listening_hours": 90,
                "current_listening_hours": 90,
                "late_night_percentage": 0,
                "baseline_valence": 0.5,
                "current_valence": 0.5,
                "repeat_listening_percentage": 0,
            }
    else:
        # No Spotify access - use neutral defaults
        spotify_metrics = {
            "baseline_listening_hours": 90,
            "current_listening_hours": 90,
            "late_night_percentage": 0,
            "baseline_valence": 0.5,
            "current_valence": 0.5,
            "repeat_listening_percentage": 0,
        }

    # Analyze Calendar patterns if token provided
    if calendar_token:
        try:
            calendar_tool = CalendarTool(calendar_token)

            # Get social patterns
            social_patterns = await calendar_tool.analyze_social_patterns(
                days_back=30,
                baseline_frequency=(
                    baseline_data.get("social_event_frequency", 8) if baseline_data else 8
                ),
            )

            # Get declined invitations
            declined_data = await calendar_tool.get_declined_invitations(days_back=30)

            # Get recurring contacts
            contacts_data = await calendar_tool.identify_recurring_contacts(days_back=60)

            # Build calendar metrics for RiskCalculator
            baseline_events = baseline_data.get("social_event_frequency", 8) if baseline_data else 8

            calendar_metrics = {
                "baseline_social_events": baseline_events,
                "current_social_events": social_patterns.get("social_event_count", 8),
                "declined_invitation_rate": declined_data.get("decline_rate", 0),
                "declined_invitations_count": declined_data.get("declined_count", 0),
                "baseline_unique_contacts": 5,  # Default
                "current_unique_contacts": len(contacts_data.get("recurring_contacts", [])),
            }

        except Exception as e:
            print(f"Error analyzing Calendar patterns: {e}")
            # Use defaults on error
            calendar_metrics = {
                "baseline_social_events": 8,
                "current_social_events": 8,
                "declined_invitation_rate": 0,
                "declined_invitations_count": 0,
                "baseline_unique_contacts": 5,
                "current_unique_contacts": 5,
            }
    else:
        # No Calendar access - use neutral defaults
        calendar_metrics = {
            "baseline_social_events": 8,
            "current_social_events": 8,
            "declined_invitation_rate": 0,
            "declined_invitations_count": 0,
            "baseline_unique_contacts": 5,
            "current_unique_contacts": 5,
        }

    # Calculate overall risk score using RiskCalculator
    risk_assessment = await calculate_loneliness_risk_score(
        user_id=user_id,
        spotify_metrics=spotify_metrics,
        calendar_metrics=calendar_metrics,
        baseline_data=baseline_data,
    )

    return {
        "risk_assessment": risk_assessment,
        "spotify_metrics": spotify_metrics,
        "calendar_metrics": calendar_metrics,
    }
