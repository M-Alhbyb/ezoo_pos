"""
SalePayment SQLAlchemy model.

Defines the breakdown of payments for a Sale.
"""

from sqlalchemy import Column, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class SalePayment(BaseModel):
    """
    SalePayment model for split payments.

    Constitution IV (Immutable Financial Records):
    - Payments are fixed at sale creation time.
    """

    __tablename__ = "sale_payments"

    sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True
    )
    payment_method_id = Column(
        UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False, index=True
    )
    amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Relationships
    sale = relationship("Sale", back_populates="payments")
    payment_method = relationship("PaymentMethod")

    @property
    def payment_method_name(self):
        return self.payment_method.name if self.payment_method else None

    def __repr__(self):
        return f"<SalePayment {self.id} - Sale: {self.sale_id} - {self.amount}>"
