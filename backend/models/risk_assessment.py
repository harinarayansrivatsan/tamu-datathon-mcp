"""
Risk Assessment model for storing loneliness risk scores.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class RiskAssessment(Base):
    """
    Risk Assessment model representing a user's loneliness risk score.
    Scores range from 0-100 with corresponding risk levels.
    """

    __tablename__ = "risk_assessments"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Risk scoring
    score = Column(Integer, nullable=False)  # 0-100
    level = Column(String(20), nullable=False)  # low, moderate, elevated, high, critical

    # Contributing factors
    factors = Column(JSON, nullable=True)  # Detailed breakdown of risk factors
    """
    Example factors structure:
    {
        "social_decline": 25,      # Score contribution from social event decline
        "mood_shift": 15,          # Score contribution from mood changes
        "communication_drop": 20,  # Score contribution from reduced communication
        "seasonal_effect": 10,     # Score contribution from weather/season
        "coding_intensity": 5      # Score contribution from late-night coding
    }
    """

    # Timestamps
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, user_id={self.user_id}, score={self.score}, level={self.level})>"

    def to_dict(self):
        """Convert risk assessment to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "score": self.score,
            "level": self.level,
            "factors": self.factors,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None,
        }


class RiskCalculator:
    """
    Risk Calculator for fusing Spotify + Calendar signals into a single risk score.

    Weights:
    - Spotify signals: 40%
    - Calendar signals: 50%
    - Baseline risk: 10%

    Risk Categories:
    - 0-25: Low risk (normal social patterns)
    - 26-50: Mild concern (slight withdrawal)
    - 51-75: Moderate risk (clear isolation pattern)
    - 76-100: High risk (severe isolation + crisis resources needed)
    """

    # Weight distributions
    SPOTIFY_WEIGHT = 0.4
    CALENDAR_WEIGHT = 0.5
    BASELINE_WEIGHT = 0.1

    # Risk category thresholds
    RISK_CATEGORIES = {
        "low": (0, 25),
        "mild": (26, 50),
        "moderate": (51, 75),
        "high": (76, 100),
    }

    @staticmethod
    def calculate_spotify_score(spotify_metrics: Dict[str, Any]) -> float:
        """
        Calculate risk score from Spotify metrics (0-100 scale).

        Components (all scale to 100-point scale):
        - Listening spike factor (37.5% of 100)
        - Late night percentage (25% of 100)
        - Valence decline factor (25% of 100)
        - Repeat listening factor (12.5% of 100)

        Total: 100 points max
        """
        score = 0.0

        # Listening spike factor (37.5 points max)
        # If current hours > baseline hours, calculate spike
        baseline_hours = spotify_metrics.get("baseline_listening_hours", 15)
        current_hours = spotify_metrics.get("current_listening_hours", 15)

        if baseline_hours > 0:
            listening_spike_ratio = current_hours / baseline_hours
            # Ratio > 2 = concerning (37.5 points), ratio 1-2 = gradual (scaled)
            if listening_spike_ratio > 2:
                score += 37.5
            elif listening_spike_ratio > 1:
                score += (listening_spike_ratio - 1) * 37.5

        # Late night percentage (25 points max)
        late_night_pct = spotify_metrics.get("late_night_percentage", 0)
        # >50% late night = 25 points, scaled linearly
        score += min(25, (late_night_pct / 50) * 25)

        # Valence decline factor (25 points max)
        baseline_valence = spotify_metrics.get("baseline_valence", 0.5)
        current_valence = spotify_metrics.get("current_valence", 0.5)
        valence_decline = baseline_valence - current_valence

        # Decline >0.3 = 25 points, scaled
        if valence_decline > 0:
            score += min(25, (valence_decline / 0.3) * 25)

        # Repeat listening factor (12.5 points max)
        repeat_percentage = spotify_metrics.get("repeat_listening_percentage", 0)
        # >40% repeat listening = 12.5 points, scaled
        score += min(12.5, (repeat_percentage / 40) * 12.5)

        return min(100, score)  # Cap at 100

    @staticmethod
    def calculate_calendar_score(calendar_metrics: Dict[str, Any]) -> float:
        """
        Calculate risk score from Calendar metrics (0-100 scale).

        Components (all scale to 100-point scale):
        - Event decline factor (50% of 100)
        - Declined invitation rate (30% of 100)
        - Friend contact decline (20% of 100)

        Total: 100 points max
        """
        score = 0.0

        # Event decline factor (50 points max)
        baseline_events = calendar_metrics.get("baseline_social_events", 8)
        current_events = calendar_metrics.get("current_social_events", 8)

        if baseline_events > 0:
            decline_ratio = (baseline_events - current_events) / baseline_events
            # 75%+ decline = 50 points, scaled
            score += min(50, decline_ratio * 66.67)

        # Declined invitation rate (30 points max)
        declined_rate = calendar_metrics.get("declined_invitation_rate", 0)
        # >50% decline rate = 30 points, scaled
        score += min(30, (declined_rate / 50) * 30)

        # Friend contact decline (20 points max)
        baseline_unique_contacts = calendar_metrics.get("baseline_unique_contacts", 5)
        current_unique_contacts = calendar_metrics.get("current_unique_contacts", 5)

        if baseline_unique_contacts > 0:
            contact_decline_ratio = (
                baseline_unique_contacts - current_unique_contacts
            ) / baseline_unique_contacts
            # 50%+ decline = 20 points, scaled
            score += min(20, (contact_decline_ratio / 0.5) * 20)

        return min(100, score)  # Cap at 100

    @staticmethod
    def calculate_baseline_risk(baseline_data: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate baseline risk score (0-100 scale).

        Uses historical risk if available, otherwise defaults to 10 (everyone starts with baseline risk).
        This provides a small baseline contribution to account for general mental health trends.
        """
        if not baseline_data:
            return 10.0

        historical_risk = baseline_data.get("historical_risk", 10)
        return min(100, max(0, historical_risk))

    @classmethod
    def calculate_risk(
        cls,
        spotify_metrics: Dict[str, Any],
        calendar_metrics: Dict[str, Any],
        baseline_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive loneliness risk score (0-100).

        Args:
            spotify_metrics: Spotify listening pattern data
            calendar_metrics: Google Calendar social event data
            baseline_data: User's baseline behavioral data

        Returns:
            Dictionary with:
            - score: int (0-100)
            - level: str (low, mild, moderate, high)
            - factors: dict (breakdown of contributing factors)
            - explanation: list of human-readable strings
        """
        # Calculate component scores
        spotify_score = cls.calculate_spotify_score(spotify_metrics)
        calendar_score = cls.calculate_calendar_score(calendar_metrics)
        baseline_score = cls.calculate_baseline_risk(baseline_data)

        # Apply weights and calculate total
        total_score = (
            (spotify_score * cls.SPOTIFY_WEIGHT)
            + (calendar_score * cls.CALENDAR_WEIGHT)
            + (baseline_score * cls.BASELINE_WEIGHT)
        )

        # Clamp to 0-100
        total_score = min(100, max(0, total_score))

        # Determine risk level
        risk_level = cls.get_risk_level(total_score)

        # Build factors breakdown
        factors = {
            "spotify_score": round(spotify_score, 2),
            "calendar_score": round(calendar_score, 2),
            "baseline_score": round(baseline_score, 2),
            "total_score": round(total_score, 2),
        }

        # Generate human-readable explanation
        explanation = cls.generate_risk_explanation(spotify_metrics, calendar_metrics, factors)

        return {
            "score": int(round(total_score)),
            "level": risk_level,
            "factors": factors,
            "explanation": explanation,
        }

    @classmethod
    def get_risk_level(cls, score: float) -> str:
        """
        Determine risk level from numeric score.

        Args:
            score: Risk score (0-100)

        Returns:
            Risk level category (low, mild, moderate, high)
        """
        for level, (min_score, max_score) in cls.RISK_CATEGORIES.items():
            if min_score <= score <= max_score:
                return level
        return "unknown"

    @staticmethod
    def generate_risk_explanation(
        spotify_metrics: Dict[str, Any],
        calendar_metrics: Dict[str, Any],
        factors: Dict[str, Any],
    ) -> List[str]:
        """
        Generate human-readable explanation of risk factors.

        Args:
            spotify_metrics: Spotify listening data
            calendar_metrics: Calendar social event data
            factors: Calculated risk factor scores

        Returns:
            List of human-readable strings explaining contributing factors
        """
        explanations = []

        # Spotify explanations
        baseline_hours = spotify_metrics.get("baseline_listening_hours", 15)
        current_hours = spotify_metrics.get("current_listening_hours", 15)

        if current_hours > baseline_hours * 1.5:
            explanations.append(
                f"Listening hours increased significantly ({baseline_hours:.1f}h → {current_hours:.1f}h)"
            )

        late_night_pct = spotify_metrics.get("late_night_percentage", 0)
        if late_night_pct > 40:
            explanations.append(
                f"{late_night_pct:.0f}% of listening happens late at night (11pm-4am)"
            )

        baseline_valence = spotify_metrics.get("baseline_valence", 0.5)
        current_valence = spotify_metrics.get("current_valence", 0.5)
        valence_decline = baseline_valence - current_valence

        if valence_decline > 0.2:
            explanations.append(
                f"Music mood shifted to sadder songs (positivity: {baseline_valence:.2f} → {current_valence:.2f})"
            )

        repeat_pct = spotify_metrics.get("repeat_listening_percentage", 0)
        if repeat_pct > 30:
            explanations.append(
                f"Frequently replaying same songs ({repeat_pct:.0f}% repeat listening)"
            )

        # Calendar explanations
        baseline_events = calendar_metrics.get("baseline_social_events", 8)
        current_events = calendar_metrics.get("current_social_events", 8)

        if current_events < baseline_events:
            decline_pct = ((baseline_events - current_events) / baseline_events) * 100
            explanations.append(
                f"Social events declined {decline_pct:.0f}% ({baseline_events} → {current_events} events/month)"
            )

        declined_invitations = calendar_metrics.get("declined_invitations_count", 0)
        if declined_invitations > 0:
            explanations.append(f"Declined {declined_invitations} social invitation(s) this month")

        baseline_contacts = calendar_metrics.get("baseline_unique_contacts", 5)
        current_contacts = calendar_metrics.get("current_unique_contacts", 5)

        if current_contacts < baseline_contacts * 0.7:
            explanations.append(
                f"Reduced contact with friends ({baseline_contacts} → {current_contacts} unique contacts)"
            )

        # If no specific concerns found
        if not explanations:
            explanations.append("No significant isolation patterns detected")

        return explanations
