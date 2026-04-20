"""
SaleFee SQLAlchemy model.

Defines the SaleFee entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class SaleFee(BaseModel):
    """
    SaleFee model for extra fees on a sale.

    Constitution III (Explicit Over Implicit):
    - fee_type, fee_label, fee_value_type, fee_value all stored explicitly
    - calculated_amount stored separately for audit trail
    """

    __tablename__ = "sale_fees"

    # Primary fields
    sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True
    )
    fee_type = Column(
        String(20), nullable=False
    )  # 'shipping', 'installation', 'custom'
    fee_label = Column(String(100), nullable=False)  # Display label
    fee_value_type = Column(String(10), nullable=False)  # 'fixed' or 'percent'
    fee_value = Column(Numeric(12, 2), nullable=False)  # Input value
    calculated_amount = Column(
        Numeric(12, 2), nullable=False
    )  # Final calculated amount

    # Relationships
    sale = relationship("Sale", back_populates="fees")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    __table_args__ = (
        CheckConstraint("fee_value >= 0", name="check_fee_value_nonnegative"),
        CheckConstraint(
            "calculated_amount >= 0", name="check_calculated_amount_nonnegative"
        ),
    )

    def __repr__(self):
        return f"<SaleFee {self.fee_label}: {self.calculated_amount}>"

    def to_dict(self):
        """Convert sale fee to dictionary for API responses."""
        return {
            "id": str(self.id),
            "sale_id": str(self.sale_id),
            "fee_type": self.fee_type,
            "fee_label": self.fee_label,
            "fee_value_type": self.fee_value_type,
            "fee_value": str(self.fee_value),
            "calculated_amount": str(self.calculated_amount),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
