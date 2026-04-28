"""
Settings SQLAlchemy model.

Defines the Settings entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Numeric
from app.core.db_types import GUID
import uuid

from app.core.database import BaseModel


class Settings(BaseModel):
    """
    Settings model for system configuration.

    Phase 0 foundation model (created during initial setup).
    """

    __tablename__ = "settings"

    # Primary fields
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    def __repr__(self):
        return f"<Settings {self.key}={self.value}>"

    def to_dict(self):
        """Convert setting to dictionary for API responses."""
        return {
            "id": str(self.id),
            "key": self.key,
            "value": self.value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
