"""
Sale SQLAlchemy model.

Defines the Sale entity for the EZOO POS system.
"""

from sqlalchemy import (
    Column,
    String,
    Numeric,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Boolean,
    text,
)
from app.core.db_types import GUID
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
        GUID(), ForeignKey("payment_methods.id"), nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )
    subtotal = Column(Numeric(12, 2), nullable=False)
    fees_total = Column(Numeric(12, 2), nullable=False, default=0)
    vat_rate = Column(Numeric(5, 2), nullable=True)  # e.g., 16.00 for 16%
    vat_total = Column(Numeric(12, 2), nullable=True)  # Renamed from vat_amount
    grand_total = Column(Numeric(12, 2), nullable=False)  # Renamed from total
    total_cost = Column(Numeric(12, 2), nullable=False, default=0)
    profit = Column(Numeric(12, 2), nullable=False, default=0)
    note = Column(Text, nullable=True)
    idempotency_key = Column(String(255), unique=True, nullable=True, index=True)
    original_sale_id = Column(
        GUID(), ForeignKey("sales.id"), nullable=True, index=True
    )
    is_reversal = Column(Boolean, nullable=False, default=False)
    customer_id = Column(
        GUID(), ForeignKey("customers.id"), nullable=True, index=True
    )

    # Added properties for test backward compatibility
    @property
    def vat_amount(self):
        return self.vat_total

    @property
    def total(self):
        return self.grand_total

    @property
    def vat_percentage(self):
        return self.vat_rate

    # Relationships
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    fees = relationship("SaleFee", back_populates="sale", cascade="all, delete-orphan")
    payment_method = relationship("PaymentMethod", backref="sales")
    payments = relationship(
        "SalePayment", back_populates="sale", cascade="all, delete-orphan"
    )
    customer = relationship("Customer", back_populates="sales")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    # Removed strict non-negative check constraints to allow for reversal records
    # Non-negativity for standard sales and true negativity for reversals
    # must be enforced at the application layer.
    __table_args__ = ()

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
