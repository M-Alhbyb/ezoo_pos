from sqlalchemy import Column, Integer, Numeric, ForeignKey, text
from app.core.db_types import GUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    purchase_id = Column(
        GUID(),
        ForeignKey("purchases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        GUID(),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", backref="purchase_items")

    @property
    def product_name(self):
        return self.product.name if self.product else None

    @property
    def product_sku(self):
        return self.product.sku if self.product else None

    @property
    def current_stock(self):
        return self.product.stock_quantity if self.product else 0
