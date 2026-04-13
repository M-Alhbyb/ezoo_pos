"""
Product SQLAlchemy model.

Defines the Product entity for the EZOO POS system.
"""

from sqlalchemy import Column, String, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import BaseModel


class Product(BaseModel):
    """
    Product model for catalog management.

    Constitution VI (Data Integrity):
    - All monetary columns use DECIMAL type
    - CHECK constraints enforce non-negative prices and stock
    - Exensibility columns (user_id, branch_id) for future multi-tenant support
    """

    __tablename__ = "products"

    # Primary fields
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=True, index=True)
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False, index=True
    )

    # Pricing
    base_price = Column(Numeric(12, 2), nullable=False)  # Cost to acquire
    selling_price = Column(Numeric(12, 2), nullable=False)  # Price charged to customers

    # Inventory
    stock_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Relationships
    category = relationship("Category", backref="products")
    partner_id = Column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="SET NULL"), nullable=True, index=True
    )
    partner = relationship("Partner", backref="products")

    # Extensibility (for future multi-user/multi-branch support)
    # user_id and branch_id inherited from BaseModel

    def __repr__(self):
        return f"<Product {self.name} (SKU: {self.sku})>"

    @property
    def profit_per_unit(self):
        """Calculate profit per unit (selling_price - base_price)."""
        return self.selling_price - self.base_price

    @property
    def is_in_stock(self):
        """Check if product has stock available."""
        return self.stock_quantity > 0

    @property
    def category_name(self):
        """Return category name if category is loaded."""
        return self.category.name if self.category else None

    @property
    def partner_name(self):
        """Return partner name if partner is loaded."""
        return self.partner.name if self.partner else None

    def to_dict(self):
        """Convert product to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "sku": self.sku,
            "category_id": str(self.category_id),
            "partner_id": str(self.partner_id) if self.partner_id else None,
            "base_price": float(self.base_price),
            "selling_price": float(self.selling_price),
            "stock_quantity": self.stock_quantity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
