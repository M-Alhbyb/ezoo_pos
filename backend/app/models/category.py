"""
Category SQLAlchemy model.

Defines the Category entity for the EZOO POS system.
"""

from sqlalchemy import Column, String
from app.core.db_types import GUID
import uuid

from app.core.database import BaseModel


class Category(BaseModel):
    """
    Category model for product organization.

    Constitution VI (Data Integrity):
    - name is unique and required
    - Extensibility columns (user_id, branch_id) for future multi-tenant support
    """

    __tablename__ = "categories"

    # Primary fields
    name = Column(String(100), nullable=False, unique=True, index=True)
    color = Column(String(50), nullable=True)

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        """Convert category to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
