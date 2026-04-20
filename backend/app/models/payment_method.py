"""
PaymentMethod SQLAlchemy model.

Defines the PaymentMethod entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import BaseModel


class PaymentMethod(BaseModel):
    """
    PaymentMethod model for payment options.

    Phase 0 foundation model (created during initial setup).
    """

    __tablename__ = "payment_methods"

    # Primary fields
    name = Column(String(50), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    def __repr__(self):
        return f"<PaymentMethod {self.name}>"

    def to_dict(self):
        """Convert payment method to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
