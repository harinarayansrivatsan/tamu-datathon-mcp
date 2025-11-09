"""
Intervention model for storing generated interventions and recommendations.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Text, func
from sqlalchemy.orm import Session, relationship

from .database import Base


class Intervention(Base):
    """
    Intervention model representing a generated intervention or recommendation.
    """

    __tablename__ = "interventions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Intervention details
    risk_score = Column(Integer, nullable=False)  # Score at time of intervention
    suggestion = Column(Text, nullable=False)  # Generated suggestion text
    event_id = Column(String(255), nullable=True)  # Associated event ID (if any)
    event_source = Column(String(50), nullable=True)  # "meetup", "eventbrite", "tamu", etc.

    # User interaction
    accepted = Column(String(10), nullable=True)  # "true", "false", or None (not responded)
    feedback = Column(Text, nullable=True)  # Optional user feedback

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interventions")

    def __repr__(self):
        return f"<Intervention(id={self.id}, user_id={self.user_id}, risk_score={self.risk_score})>"

    def to_dict(self):
        """Convert intervention to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "risk_score": self.risk_score,
            "suggestion": self.suggestion,
            "event_id": self.event_id,
            "event_source": self.event_source,
            "accepted": self.accepted == "true" if self.accepted else None,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
        }


# Intervention Tracking Functions


def store_intervention(
    db: Session,
    user_id: str,
    risk_score: int,
    suggestion: str,
    event_id: Optional[str] = None,
    event_source: Optional[str] = None,
) -> Intervention:
    """
    Store a new intervention in the database.

    Args:
        db: Database session
        user_id: User ID
        risk_score: Risk score at time of intervention (0-100)
        suggestion: Generated intervention text
        event_id: Optional event ID if recommending a specific event
        event_source: Optional event source (meetup, eventbrite, etc.)

    Returns:
        Created Intervention object
    """
    intervention = Intervention(
        user_id=user_id,
        risk_score=risk_score,
        suggestion=suggestion,
        event_id=event_id,
        event_source=event_source,
    )

    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    return intervention


def track_user_engagement(
    db: Session,
    intervention_id: str,
    accepted: bool,
    feedback: Optional[str] = None,
) -> Optional[Intervention]:
    """
    Track user engagement with an intervention.

    Args:
        db: Database session
        intervention_id: Intervention ID
        accepted: Whether user accepted the suggestion
        feedback: Optional user feedback text

    Returns:
        Updated Intervention object or None if not found
    """
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()

    if not intervention:
        return None

    intervention.accepted = "true" if accepted else "false"
    intervention.feedback = feedback
    intervention.responded_at = datetime.utcnow()

    db.commit()
    db.refresh(intervention)

    return intervention


def measure_intervention_effectiveness(
    db: Session,
    user_id: str,
    current_risk_score: int,
    lookback_days: int = 7,
) -> Dict[str, any]:
    """
    Measure effectiveness of interventions for a user.

    Compares current risk score with risk scores at time of interventions
    to determine if interventions are helping.

    Args:
        db: Database session
        user_id: User ID
        current_risk_score: Current risk score
        lookback_days: Number of days to look back (default: 7)

    Returns:
        Dictionary with effectiveness metrics:
        - total_interventions: Total interventions in lookback period
        - accepted_count: Number of accepted interventions
        - declined_count: Number of declined interventions
        - no_response_count: Number with no response
        - average_previous_risk: Average risk score when interventions were created
        - risk_change: Change in risk score (negative = improvement)
        - effectiveness_score: 0-100 score (higher = more effective)
        - trend: "improving", "stable", or "declining"
    """
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

    # Get interventions in lookback period
    interventions = (
        db.query(Intervention)
        .filter(
            Intervention.user_id == user_id,
            Intervention.created_at >= cutoff_date,
        )
        .all()
    )

    total_interventions = len(interventions)

    if total_interventions == 0:
        return {
            "total_interventions": 0,
            "accepted_count": 0,
            "declined_count": 0,
            "no_response_count": 0,
            "average_previous_risk": None,
            "risk_change": None,
            "effectiveness_score": None,
            "trend": "insufficient_data",
        }

    # Count engagement
    accepted_count = sum(1 for i in interventions if i.accepted == "true")
    declined_count = sum(1 for i in interventions if i.accepted == "false")
    no_response_count = sum(1 for i in interventions if i.accepted is None)

    # Calculate average previous risk score
    average_previous_risk = sum(i.risk_score for i in interventions) / total_interventions

    # Calculate risk change (negative = improvement)
    risk_change = current_risk_score - average_previous_risk

    # Calculate effectiveness score (0-100)
    # Factors:
    # - Engagement rate (accepted vs total)
    # - Risk improvement (negative risk_change is good)
    engagement_rate = accepted_count / total_interventions if total_interventions > 0 else 0

    # Normalize risk change to 0-1 scale (improvement = higher score)
    # Risk can change by max ±100 points
    risk_improvement_factor = max(0, min(1, (-risk_change + 50) / 100))

    # Combined effectiveness score (weighted: 40% engagement, 60% risk improvement)
    effectiveness_score = int((engagement_rate * 40) + (risk_improvement_factor * 60))

    # Determine trend
    if risk_change < -10:
        trend = "improving"
    elif risk_change > 10:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "total_interventions": total_interventions,
        "accepted_count": accepted_count,
        "declined_count": declined_count,
        "no_response_count": no_response_count,
        "average_previous_risk": round(average_previous_risk, 2),
        "risk_change": round(risk_change, 2),
        "effectiveness_score": effectiveness_score,
        "trend": trend,
    }


def get_user_intervention_history(
    db: Session,
    user_id: str,
    limit: int = 10,
) -> List[Intervention]:
    """
    Get intervention history for a user.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of interventions to return (default: 10)

    Returns:
        List of Intervention objects, ordered by most recent first
    """
    interventions = (
        db.query(Intervention)
        .filter(Intervention.user_id == user_id)
        .order_by(Intervention.created_at.desc())
        .limit(limit)
        .all()
    )

    return interventions


def get_intervention_stats(db: Session, user_id: str) -> Dict[str, any]:
    """
    Get overall intervention statistics for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with overall statistics
    """
    all_interventions = db.query(Intervention).filter(Intervention.user_id == user_id).all()

    if not all_interventions:
        return {
            "total_interventions": 0,
            "acceptance_rate": None,
            "average_risk_score": None,
            "first_intervention_date": None,
            "last_intervention_date": None,
        }

    total = len(all_interventions)
    accepted = sum(1 for i in all_interventions if i.accepted == "true")
    acceptance_rate = (accepted / total * 100) if total > 0 else 0

    risk_scores = [i.risk_score for i in all_interventions]
    average_risk = sum(risk_scores) / len(risk_scores)

    dates = [i.created_at for i in all_interventions if i.created_at]
    first_date = min(dates) if dates else None
    last_date = max(dates) if dates else None

    return {
        "total_interventions": total,
        "acceptance_rate": round(acceptance_rate, 2),
        "average_risk_score": round(average_risk, 2),
        "first_intervention_date": first_date.isoformat() if first_date else None,
        "last_intervention_date": last_date.isoformat() if last_date else None,
    }
