"""
SaleReversal SQLAlchemy model.

Defines the SaleReversal entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class SaleReversal(BaseModel):
    """
    SaleReversal model for linking original sales to their reversals.

    Constitution IV (Immutable Financial Records):
    - Tracks which sales have been reversed
    - Prevents double reversals
    - Maintains audit trail
    """

    __tablename__ = "sale_reversals"

    # Primary fields
    original_sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True
    )
    reversal_sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id"), nullable=True)
    reason = Column(Text, nullable=False)

    # Relationships
    original_sale = relationship("Sale", foreign_keys=[original_sale_id])
    reversal_sale = relationship("Sale", foreign_keys=[reversal_sale_id])

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    def __repr__(self):
        return f"<SaleReversal {self.original_sale_id} -> {self.reversal_sale_id}>"

    def to_dict(self):
        """Convert sale reversal to dictionary for API responses."""
        return {
            "id": str(self.id),
            "original_sale_id": str(self.original_sale_id),
            "reversal_sale_id": str(self.reversal_sale_id)
            if self.reversal_sale_id
            else None,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
