# pyright: reportMissingImports=false
"""API key storage model."""

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from paystreet.app.database import Base
from paystreet.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ApiKey(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores provider API keys managed via the admin dashboard."""

    __tablename__ = "api_keys"

    # e.g. "openai", "elevenlabs"
    provider: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    # Encrypted/plain key value — stored as text
    key_value: Mapped[str] = mapped_column(Text, nullable=False)
    # Human-readable label, e.g. "GPT-4o key"
    label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
