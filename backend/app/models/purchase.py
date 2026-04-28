from sqlalchemy import Column, Numeric, DateTime, ForeignKey, text
from app.core.db_types import GUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    supplier_id = Column(
        GUID(),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    total_amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    supplier = relationship("Supplier", backref="purchases")
    items = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )
