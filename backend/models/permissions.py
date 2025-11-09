"""
Permission model for managing user data source permissions.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from .database import Base
from backend.core.encryption import encrypt_token, decrypt_token


class Permission(Base):
    """
    Permission model representing user's data source access permissions.
    Privacy-first design: explicit opt-in required for each data source.
    """

    __tablename__ = "permissions"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # Data source permissions (stored as "true"/"false" strings for SQLite compatibility)
    calendar_enabled = Column(String(10), default="false", nullable=False)
    spotify_enabled = Column(String(10), default="false", nullable=False)
    github_enabled = Column(String(10), default="false", nullable=False)
    weather_enabled = Column(String(10), default="false", nullable=False)
    discord_enabled = Column(String(10), default="false", nullable=False)

    # OAuth tokens (encrypted in production)
    google_access_token = Column(String(500), nullable=True)
    google_refresh_token = Column(String(500), nullable=True)
    spotify_access_token = Column(String(500), nullable=True)
    spotify_refresh_token = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="permissions")

    def __repr__(self):
        return f"<Permission(id={self.id}, user_id={self.user_id})>"

    def to_dict(self):
        """Convert permissions to dictionary for API responses (excludes tokens)."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "calendar_enabled": self.calendar_enabled == "true",
            "spotify_enabled": self.spotify_enabled == "true",
            "github_enabled": self.github_enabled == "true",
            "weather_enabled": self.weather_enabled == "true",
            "discord_enabled": self.discord_enabled == "true",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def has_permission(self, source: str) -> bool:
        """Check if a specific data source is enabled."""
        field = f"{source}_enabled"
        if hasattr(self, field):
            return getattr(self, field) == "true"
        return False

    def set_permission(self, source: str, enabled: bool):
        """Set permission for a specific data source."""
        field = f"{source}_enabled"
        if hasattr(self, field):
            setattr(self, field, "true" if enabled else "false")

    def set_google_token(self, token: str):
        """Set Google access token with encryption."""
        self.google_access_token = encrypt_token(token) if token else None

    def get_google_token(self) -> str:
        """Get decrypted Google access token."""
        return decrypt_token(self.google_access_token) if self.google_access_token else ""

    def set_spotify_token(self, token: str):
        """Set Spotify access token with encryption."""
        self.spotify_access_token = encrypt_token(token) if token else None

    def get_spotify_token(self) -> str:
        """Get decrypted Spotify access token."""
        return decrypt_token(self.spotify_access_token) if self.spotify_access_token else ""
