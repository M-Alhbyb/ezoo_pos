from sqlalchemy import Column, Integer, Numeric, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    purchase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        UUID(as_uuid=True),
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
