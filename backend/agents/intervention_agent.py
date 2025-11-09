"""
Intervention Agent for generating personalized, empathetic interventions.

Generates compassionate, anxiety-appropriate interventions based on the user's
risk level and personal context using Google's Gemini API.
"""

from typing import Any, Dict, List, Optional

from backend.core import get_settings
from backend.core.prompts import (
    format_intervention_prompt,
    format_crisis_prompt,
)
from backend.tools import EventMatchingTool

settings = get_settings()


async def generate_empathetic_message(
    risk_level: str, risk_score: int, user_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate an empathetic intervention message based on risk level.

    Args:
        risk_level: Risk level (low, moderate, elevated, high, critical)
        risk_score: Numerical risk score (0-100)
        user_context: Optional context about the user

    Returns:
        Empathetic message string
    """
    messages = {
        "low": """
        Hey! I've been keeping an eye on your patterns, and things look pretty steady.
        You're doing a great job maintaining your social connections. Keep it up!
        """,
        "moderate": """
        I noticed you've been spending a bit more time solo lately - totally normal,
        especially if you're in the middle of exams or busy season. Just wanted to
        check in. How are you feeling about your social energy lately?
        """,
        "elevated": """
        I've noticed some patterns that caught my attention. You used to hang out
        with people more often, and your recent listening history suggests you might
        be feeling a bit down. Not judging at all - we all go through phases. But I
        wanted to check in because I care about you. Would you be open to reconnecting
        with someone or trying a low-key social activity?
        """,
        "high": """
        Hey, I want to be real with you. I've noticed some concerning patterns -
        you've been isolating more than usual, and your mood seems to have shifted.
        I'm not here to diagnose anything, but as someone who cares about you, I think
        it might be time to reach out to someone. Whether that's a friend, a counselor,
        or just getting out of the house for a bit. You don't have to go through this alone.
        """,
        "critical": """
        I'm genuinely worried about you. The patterns I'm seeing suggest you might be
        struggling with serious isolation and possibly depression. Please, please reach
        out to someone you trust or a mental health professional. This is not something
        you should handle alone. There are people who care about you and want to help.

        Crisis Resources:
        - National Suicide Prevention Lifeline: 988
        - Crisis Text Line: Text HOME to 741741
        - TAMU Counseling & Psychological Services: (979) 845-4427
        """,
    }

    return messages.get(risk_level, messages["moderate"]).strip()


async def recommend_activities(
    risk_level: str,
    interests: Optional[List[str]] = None,
    location: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Recommend anxiety-appropriate activities based on risk level.

    Args:
        risk_level: User's risk level
        interests: User's interests (None if not available)
        location: User's location (None if not available)

    Returns:
        List of recommended activities (empty if data unavailable)
    """
    # Don't fake data - return empty if missing critical info
    if not interests or not location:
        print("Cannot recommend activities: missing interests or location")
        return []

    # Map risk level to anxiety level for event matching
    anxiety_mapping = {
        "low": "low",
        "moderate": "low",
        "elevated": "medium",
        "high": "high",
        "critical": "high",
    }

    anxiety_level = anxiety_mapping.get(risk_level, "medium")

    try:
        event_tool = EventMatchingTool()
        recommendations = await event_tool.recommend_events(
            location=location,
            anxiety_level=anxiety_level,
            interests=interests,
            limit=5,
        )

        return recommendations

    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []


async def generate_intervention_strategy(
    risk_assessment: Dict[str, Any],
    user_interests: Optional[List[str]] = None,
    user_location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a complete intervention strategy.

    Args:
        risk_assessment: Risk assessment from detection agent
        user_interests: User's interests
        user_location: User's location

    Returns:
        Complete intervention strategy dictionary
    """
    risk_level = risk_assessment.get("level", "moderate")
    risk_score = risk_assessment.get("score", 50)

    # Generate empathetic message
    message = await generate_empathetic_message(
        risk_level=risk_level,
        risk_score=risk_score,
    )

    # Recommend activities (only for non-critical levels)
    activities = []
    if risk_level != "critical":
        activities = await recommend_activities(
            risk_level=risk_level,
            interests=user_interests,
            location=user_location,
        )

    # Generate specific action items
    action_items = []

    if risk_level in ["low", "moderate"]:
        action_items = [
            "Continue maintaining your current social connections",
            "Consider trying one new social activity this week",
        ]
    elif risk_level == "elevated":
        action_items = [
            "Reach out to a friend you haven't talked to in a while",
            "Join one small group activity (see recommendations below)",
            "Spend 10 minutes outside in a social space (coffee shop, park)",
        ]
    elif risk_level == "high":
        action_items = [
            "Text or call one person you trust today",
            "Schedule a low-pressure social activity within 3 days",
            "Consider talking to a counselor or therapist",
            "Join a structured group activity (less awkward than 'just hanging out')",
        ]
    elif risk_level == "critical":
        action_items = [
            "Call or text someone you trust RIGHT NOW",
            "Contact TAMU Counseling Services: (979) 845-4427",
            "Call National Suicide Prevention Lifeline: 988",
            "Go to a public place (don't stay isolated)",
        ]

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "message": message,
        "activities": activities,
        "action_items": action_items,
    }


async def run_intervention(
    risk_assessment: Dict[str, Any],
    user_id: Optional[str] = None,
    user_interests: Optional[List[str]] = None,
    user_location: Optional[str] = None,
    user_message: Optional[str] = None,
    db_session: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Run the intervention agent to generate personalized intervention using Google ADK.

    Args:
        risk_assessment: Risk assessment from detection agent
        user_id: User ID for tracking (None if not available)
        user_interests: User's interests (None if not available)
        user_location: User's location (None if not available)
        user_message: Optional message from the user
        db_session: Database session for storing intervention (None if not available)

    Returns:
        Intervention strategy dictionary with LLM-generated response
    """
    risk_level = risk_assessment.get("level", "moderate")
    risk_score = risk_assessment.get("score", 50)
    factors = risk_assessment.get("factors", {})

    # Get event recommendations
    activities = []
    if risk_level != "critical":
        activities = await recommend_activities(
            risk_level=risk_level,
            interests=user_interests,
            location=user_location,
        )

    # Generate action items based on risk level
    action_items = []
    if risk_level in ["low", "moderate"]:
        action_items = [
            "Continue maintaining your current social connections",
            "Consider trying one new social activity this week",
        ]
    elif risk_level == "elevated":
        action_items = [
            "Reach out to a friend you haven't talked to in a while",
            "Join one small group activity (see recommendations below)",
            "Spend 10 minutes outside in a social space (coffee shop, park)",
        ]
    elif risk_level == "high":
        action_items = [
            "Text or call one person you trust today",
            "Schedule a low-pressure social activity within 3 days",
            "Consider talking to a counselor or therapist",
            "Join a structured group activity (less awkward than 'just hanging out')",
        ]
    elif risk_level == "critical":
        action_items = [
            "Call or text someone you trust RIGHT NOW",
            "Contact TAMU Counseling Services: (979) 845-4427",
            "Call National Suicide Prevention Lifeline: 988",
            "Go to a public place (don't stay isolated)",
        ]

    # Construct prompt using templates
    # Extract friend list and days since social event from factors
    friend_list = factors.get("recurring_contacts", []) if isinstance(factors, dict) else []
    days_since_social = (
        factors.get("days_since_social_event") if isinstance(factors, dict) else None
    )

    # Format risk explanation from factors
    if isinstance(factors, dict):
        risk_explanation = "\n".join(f"- {k}: {v}" for k, v in factors.items())
    else:
        risk_explanation = str(factors)

    # Use crisis prompt for high-risk scores (76-100)
    if risk_score >= 76:
        risk_factors_list = []
        if isinstance(factors, dict):
            risk_factors_list = [f"{k}: {v}" for k, v in factors.items()]
        else:
            risk_factors_list = [str(factors)]

        user_context = format_crisis_prompt(
            risk_score=risk_score,
            risk_factors=risk_factors_list,
            user_message=user_message or "User is checking in",
        )
    else:
        # Use standard intervention prompt
        user_context = format_intervention_prompt(
            risk_score=risk_score,
            risk_explanation=risk_explanation,
            user_message=user_message or "User is checking in",
            friend_list=friend_list,
            days_since_social_event=days_since_social,
        )

        # Add context about available activities and user interests
        user_context += f"\n\nAdditional Context:\n"
        user_context += f"- User Interests: {', '.join(user_interests) if user_interests else 'Not specified'}\n"
        user_context += f"- Location: {user_location}\n"
        user_context += f"- Available Activities: {len(activities)} events found matching their anxiety level and interests\n"

    try:
        # Use Google GenAI SDK to generate personalized response
        from google import genai

        print(f"🤖 Calling Gemini API with model: {settings.gemini_model_pro}")
        print(f"🔑 API Key present: {bool(settings.google_api_key)}")
        print(f"📝 User context length: {len(user_context)} chars")

        client = genai.Client(api_key=settings.google_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model_pro,
            contents=user_context,
        )
        llm_message = response.text
        print(f"✅ Gemini response received: {len(llm_message)} chars")

    except Exception as e:
        print(f"❌ Error generating LLM response: {e}")
        import traceback

        traceback.print_exc()
        # Fallback to template-based response
        print("⚠️ Falling back to template response")
        llm_message = await generate_empathetic_message(
            risk_level=risk_level,
            risk_score=risk_score,
        )

    # Store intervention in database for tracking (if db_session and user_id provided)
    intervention_id = None
    if db_session and user_id:
        try:
            from backend.models.interventions import store_intervention

            # Extract event info from activities if available
            event_id = None
            event_source = None
            if activities and len(activities) > 0:
                event_id = activities[0].get("id")
                event_source = activities[0].get("source")

            intervention = store_intervention(
                db=db_session,
                user_id=user_id,
                risk_score=risk_score,
                suggestion=llm_message,
                event_id=event_id,
                event_source=event_source,
            )
            intervention_id = intervention.id
            print(f"✅ Intervention stored: {intervention_id}")
        except Exception as e:
            print(f"⚠️ Failed to store intervention: {e}")
            # Continue without storing - don't fail the entire intervention

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "message": llm_message,
        "activities": activities,
        "action_items": action_items,
        "intervention_id": intervention_id,  # Include ID for tracking user responses
    }
