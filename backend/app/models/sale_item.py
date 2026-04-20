"""
SaleItem SQLAlchemy model.

Defines the SaleItem entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class SaleItem(BaseModel):
    """
    SaleItem model for line items within a sale.

    Constitution III (Explicit Over Implicit):
    - unit_price stored explicitly (may differ from product.selling_price)
    - product_name snapshot preserved for audit trail
    - line_total calculated and stored explicitly
    """

    __tablename__ = "sale_items"

    # Primary fields
    sale_id = Column(
        UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False, index=True
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    product_name = Column(String(200), nullable=False)  # Snapshot
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    base_cost = Column(Numeric(12, 2), nullable=True)  # Snapshot of product.base_price
    vat_rate = Column(Numeric(5, 2), nullable=True)  # Snapshot of VAT rate at time of sale
    line_total = Column(Numeric(12, 2), nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", backref="sale_items")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="check_unit_price_nonnegative"),
        CheckConstraint("base_cost >= 0", name="check_base_cost_nonnegative"),
    )

    @property
    def price(self):
        return self.unit_price

    def to_dict(self):
        """Convert sale item to dictionary for API responses."""
        return {
            "id": str(self.id),
            "sale_id": str(self.sale_id),
            "product_id": str(self.product_id),
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "line_total": str(self.line_total),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
