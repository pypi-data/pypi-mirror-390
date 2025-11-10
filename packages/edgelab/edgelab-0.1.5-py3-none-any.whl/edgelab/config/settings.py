"""Settings and configuration management for EdgeLab CLI."""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AuthTokens(BaseModel):
    """Authentication tokens."""

    access_token: str
    refresh_token: str
    expires_at: datetime


class UserInfo(BaseModel):
    """User information."""

    id: str
    email: str
    role: str = "free"


class Settings(BaseSettings):
    """EdgeLab CLI settings."""

    # API Configuration
    api_base_url: str = Field(
        default="https://pantry-chef.com",
        description="EdgeLab API base URL",
    )

    # Local directories
    edgelab_dir: Path = Field(
        default_factory=lambda: Path.home() / ".edgelab",
        description="EdgeLab config directory",
    )

    @property
    def auth_file(self) -> Path:
        """Path to auth tokens file."""
        return self.edgelab_dir / "auth.json"

    @property
    def config_file(self) -> Path:
        """Path to config file."""
        return self.edgelab_dir / "config.json"

    def ensure_dir_exists(self):
        """Ensure EdgeLab directory exists with correct permissions."""
        self.edgelab_dir.mkdir(parents=True, exist_ok=True)
        # Set directory permissions to 700 (rwx------)
        os.chmod(self.edgelab_dir, 0o700)

    def load_auth(self) -> Optional[dict]:
        """Load authentication tokens from file.

        Returns:
            Dict with access_token, refresh_token, expires_at, user
            None if not authenticated
        """
        if not self.auth_file.exists():
            return None

        try:
            with open(self.auth_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def save_auth(self, access_token: str, refresh_token: str, expires_at: str, user: dict):
        """Save authentication tokens to file.

        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token
            expires_at: ISO format expiration timestamp
            user: User info dict (id, email, role)
        """
        self.ensure_dir_exists()

        auth_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "user": user,
        }

        with open(self.auth_file, "w") as f:
            json.dump(auth_data, f, indent=2)

        # Set file permissions to 600 (rw-------)
        os.chmod(self.auth_file, 0o600)

    def clear_auth(self):
        """Clear authentication tokens."""
        if self.auth_file.exists():
            self.auth_file.unlink()

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        auth = self.load_auth()
        return auth is not None and "access_token" in auth

    def get_access_token(self) -> Optional[str]:
        """Get current access token."""
        auth = self.load_auth()
        return auth.get("access_token") if auth else None

    def get_refresh_token(self) -> Optional[str]:
        """Get current refresh token."""
        auth = self.load_auth()
        return auth.get("refresh_token") if auth else None

    def get_user(self) -> Optional[dict]:
        """Get current user info."""
        auth = self.load_auth()
        return auth.get("user") if auth else None


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
