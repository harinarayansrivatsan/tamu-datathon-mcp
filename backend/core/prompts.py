"""
Prompt templates for Loneliness Combat Engine interventions.

This module contains prompt templates for generating empathetic,
personalized interventions using Gemini.
"""

INTERVENTION_PROMPT = """
You are a compassionate friend helping someone who may be experiencing social isolation.

Risk Level: {risk_score}/100
Contributing Factors:
{risk_explanation}

User's Message: {user_message}

Friend Context:
- Recurring contacts: {friend_list}
- Last social event: {days_since_social_event} days ago

Guidelines:
- Be empathetic and non-judgmental
- Acknowledge their feelings as valid
- Provide ONE specific, actionable suggestion (e.g., text a specific friend)
- Keep tone casual (like a caring friend, not a therapist)
- For risk 76-100: Include crisis resources (988 Suicide & Crisis Lifeline)

Generate a supportive response:
"""


DETECTION_ANALYSIS_PROMPT = """
You are analyzing behavioral patterns to detect potential social isolation.

User Data:
- Calendar Events (last 30 days): {calendar_summary}
- Music Listening Patterns: {spotify_summary}
- Communication Patterns: {communication_summary}
- Baseline Behavior: {baseline_summary}

Task: Analyze the data and identify:
1. Significant deviations from baseline behavior
2. Concerning patterns (e.g., declining social events, mood shifts)
3. Contributing factors to potential isolation

Output a structured risk assessment with:
- Risk score (0-100)
- Contributing factors (list)
- Explanation of patterns noticed
"""


CRISIS_ESCALATION_PROMPT = """
URGENT: User showing signs of severe isolation (Risk Score: {risk_score}/100)

Contributing Factors:
{risk_factors}

User's Recent Message: "{user_message}"

Generate an IMMEDIATE intervention response that:
1. Expresses genuine concern and care
2. Validates their struggle without minimizing it
3. Provides IMMEDIATE crisis resources prominently:
   - National Suicide Prevention Lifeline: 988
   - Crisis Text Line: Text HOME to 741741
   - TAMU Counseling & Psychological Services: (979) 845-4427
4. Encourages reaching out to someone RIGHT NOW
5. Emphasizes they are not alone and help is available
6. Tone: urgent but caring, serious but non-judgmental

Generate the crisis intervention response:
"""


EVENT_RECOMMENDATION_PROMPT = """
You are recommending social activities for someone experiencing {anxiety_level} social anxiety.

User Profile:
- Interests: {interests}
- Location: {location}
- Social Anxiety Level: {anxiety_level}
- Recent Social Pattern: {social_pattern}

Available Events:
{events_list}

Task: Select and rank the TOP 3 most appropriate events based on:
1. Anxiety appropriateness (group size, structure, duration)
2. Interest alignment
3. Proximity and accessibility
4. Pressure level (low-pressure activities preferred)

For each recommended event, explain:
- Why it's a good match for their anxiety level
- What makes it less intimidating
- How it aligns with their interests

Generate the event recommendations:
"""


FOLLOW_UP_PROMPT = """
You are following up on a previous intervention.

Previous Intervention:
- Date: {intervention_date}
- Risk Score: {previous_risk_score}/100
- Suggestion Given: {previous_suggestion}
- User Response: {user_response}

Current Assessment:
- Current Risk Score: {current_risk_score}/100
- Pattern Changes: {pattern_changes}
- Days Since Last Social Event: {days_since_social}

Task: Generate a follow-up message that:
1. Acknowledges their previous response (if any)
2. Celebrates improvements (if risk decreased)
3. Expresses continued support (if risk increased or stayed same)
4. Provides adjusted recommendations based on current state
5. Asks if previous suggestion was helpful (gentle check-in)

Tone: Warm, consistent, non-pushy, like checking in with a friend

Generate the follow-up message:
"""


BASELINE_LEARNING_PROMPT = """
You are establishing a baseline for a new user's social behavior.

Initial Data Collection Period: {collection_period_days} days

Data Collected:
- Calendar: {calendar_summary}
- Music: {spotify_summary}
- Communication: {communication_summary}

Task: Analyze the data to establish:
1. Typical social event frequency (events per week)
2. Preferred social settings (small groups, large events, one-on-one)
3. Music mood baseline (genre preferences, listening times)
4. Communication patterns (frequency, preferred platforms)
5. Introvert/extrovert indicators

Output a baseline profile that includes:
- Social energy level (introvert/extrovert/ambivert)
- Normal social frequency
- Red flags to watch for (deviations that would indicate isolation)

Generate the baseline profile:
"""


# Prompt helper functions


def format_intervention_prompt(
    risk_score: int,
    risk_explanation: str,
    user_message: str,
    friend_list: list[str] | None = None,
    days_since_social_event: int | None = None,
) -> str:
    """
    Format the intervention prompt with user data.

    Args:
        risk_score: User's risk score (0-100)
        risk_explanation: Explanation of contributing factors
        user_message: User's message or "User is checking in"
        friend_list: List of recurring contact names
        days_since_social_event: Days since last social event

    Returns:
        Formatted prompt string
    """
    friend_str = ", ".join(friend_list) if friend_list else "No recurring contacts identified"
    days_str = str(days_since_social_event) if days_since_social_event is not None else "Unknown"

    return INTERVENTION_PROMPT.format(
        risk_score=risk_score,
        risk_explanation=risk_explanation,
        user_message=user_message,
        friend_list=friend_str,
        days_since_social_event=days_str,
    )


def format_crisis_prompt(risk_score: int, risk_factors: list[str], user_message: str = "") -> str:
    """
    Format the crisis escalation prompt.

    Args:
        risk_score: User's risk score (should be 76-100)
        risk_factors: List of contributing factors
        user_message: User's recent message

    Returns:
        Formatted crisis prompt string
    """
    factors_str = "\n".join(f"- {factor}" for factor in risk_factors)

    return CRISIS_ESCALATION_PROMPT.format(
        risk_score=risk_score,
        risk_factors=factors_str,
        user_message=user_message or "No recent message",
    )


def format_event_recommendation_prompt(
    anxiety_level: str, interests: list[str], location: str, social_pattern: str, events: list[dict]
) -> str:
    """
    Format the event recommendation prompt.

    Args:
        anxiety_level: low, medium, or high
        interests: List of user interests
        location: User location
        social_pattern: Description of recent social patterns
        events: List of event dictionaries

    Returns:
        Formatted event recommendation prompt string
    """
    interests_str = ", ".join(interests) if interests else "Not specified"
    events_str = "\n".join(
        f"- {event.get('name', 'Unknown')}: {event.get('description', 'No description')}"
        for event in events
    )

    return EVENT_RECOMMENDATION_PROMPT.format(
        anxiety_level=anxiety_level,
        interests=interests_str,
        location=location,
        social_pattern=social_pattern,
        events_list=events_str,
    )
