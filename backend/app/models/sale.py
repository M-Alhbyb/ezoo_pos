"""
Sale SQLAlchemy model.

Defines the Sale entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Numeric, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class Sale(BaseModel):
    """
    Sale model for completed transactions.

    Constitution IV (Immutable Financial Records):
    - Sale is immediately confirmed on creation
    - Immutable after creation (no updates/deletes)
    - Corrections via reversals only

    Constitution VI (Data Integrity):
    - All monetary columns use DECIMAL type
    - CHECK constraints enforce non-negative values
    """

    __tablename__ = "sales"

    # Primary fields
    payment_method_id = Column(
        UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False, index=True
    )
    subtotal = Column(Numeric(12, 2), nullable=False)
    fees_total = Column(Numeric(12, 2), nullable=False, default=0)
    vat_rate = Column(Numeric(5, 2), nullable=True)  # e.g., 16.00 for 16%
    vat_amount = Column(Numeric(12, 2), nullable=True)
    total = Column(Numeric(12, 2), nullable=False)
    note = Column(Text, nullable=True)  # Relationships
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    fees = relationship("SaleFee", back_populates="sale", cascade="all, delete-orphan")
    payment_method = relationship("PaymentMethod", backref="sales")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="check_subtotal_nonnegative"),
        CheckConstraint("fees_total >= 0", name="check_fees_total_nonnegative"),
        CheckConstraint("total >= 0", name="check_total_nonnegative"),
    )

    def __repr__(self):
        return f"<Sale {self.id} - Total: {self.total}>"

    def to_dict(self):
        """Convert sale to dictionary for API responses."""
        return {
            "id": str(self.id),
            "payment_method_id": str(self.payment_method_id),
            "subtotal": str(self.subtotal),
            "fees_total": str(self.fees_total),
            "vat_rate": str(self.vat_rate) if self.vat_rate else None,
            "vat_amount": str(self.vat_amount) if self.vat_amount else None,
            "total": str(self.total),
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
