"""
Baseline model for storing user behavioral baselines.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class Baseline(Base):
    """
    Baseline model representing a user's normal behavioral patterns.
    Established during the initial observation period (default: 14 days).
    """

    __tablename__ = "baselines"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Social event patterns
    social_event_frequency = Column(Float, nullable=True)  # Events per week
    social_event_types = Column(JSON, nullable=True)  # Types of events attended

    # Mood patterns (from Spotify)
    mood_baseline = Column(JSON, nullable=True)  # Average mood metrics
    music_patterns = Column(JSON, nullable=True)  # Listening patterns

    # Communication patterns
    communication_frequency = Column(Float, nullable=True)  # Messages per day

    # Coding patterns (for CS students)
    coding_pattern = Column(JSON, nullable=True)  # GitHub activity baseline

    # Baseline status
    is_established = Column(String(10), default="false", nullable=False)  # "true" or "false"
    observation_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    established_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="baselines")

    def __repr__(self):
        return (
            f"<Baseline(id={self.id}, user_id={self.user_id}, established={self.is_established})>"
        )

    def to_dict(self):
        """Convert baseline to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "social_event_frequency": self.social_event_frequency,
            "mood_baseline": self.mood_baseline,
            "communication_frequency": self.communication_frequency,
            "is_established": self.is_established == "true",
            "observation_start": (
                self.observation_start.isoformat() if self.observation_start else None
            ),
            "established_at": (self.established_at.isoformat() if self.established_at else None),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
