"""
User model for Loneliness Combat Engine.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """User model representing a registered user."""

    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=True)
    interests = Column(String(500), nullable=True)  # Comma-separated interests
    location = Column(String(255), nullable=True)  # User's city/location
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    baselines = relationship("Baseline", back_populates="user", cascade="all, delete-orphan")
    risk_assessments = relationship(
        "RiskAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    permissions = relationship(
        "Permission", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    interventions = relationship(
        "Intervention", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    def to_dict(self):
        """Convert user to dictionary for API responses."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "interests": self.interests,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }
