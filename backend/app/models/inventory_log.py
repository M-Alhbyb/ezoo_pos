"""
InventoryLog SQLAlchemy model.

Defines the InventoryLog entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class InventoryLog(BaseModel):
    """
    InventoryLog model for audit trail of stock changes.

    Constitution VI (Data Integrity):
    - Every stock change MUST create a log entry
    - balance_after ensures snapshot consistency
    - reference_id links to source record
    """

    __tablename__ = "inventory_log"

    # Primary fields
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    delta = Column(Integer, nullable=False)  # Quantity change (+/-)
    reason = Column(
        String(20), nullable=False
    )  # 'sale', 'reversal', 'restock', 'adjustment'
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # FK to sale or reversal
    balance_after = Column(Integer, nullable=False)  # Stock level after change

    # Relationships
    product = relationship("Product", backref="inventory_logs")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    __table_args__ = (
        CheckConstraint("balance_after >= 0", name="check_balance_nonnegative"),
    )

    def __repr__(self):
        return f"<InventoryLog {self.product_id}: {self.delta} ({self.reason})>"

    def to_dict(self):
        """Convert inventory log to dictionary for API responses."""
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "delta": self.delta,
            "reason": self.reason,
            "reference_id": str(self.reference_id) if self.reference_id else None,
            "balance_after": self.balance_after,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
