"""
ProductAssignment SQLAlchemy model.

Tracks which partner products are assigned to and their share percentages.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    text,
)
from sqlalchemy.orm import relationship

from app.core.database import BaseModel
from app.core.db_types import GUID


class ProductAssignment(BaseModel):
    """Assignment of a product to a partner with a share percentage."""

    __tablename__ = "product_assignments"

    partner_id = Column(
        GUID(), ForeignKey("partners.id"), nullable=False, index=True
    )
    product_id = Column(
        GUID(), ForeignKey("products.id"), nullable=False, index=True
    )
    assigned_quantity = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=False, server_default=text("0"))
    share_percentage = Column(Numeric(5, 2), nullable=False)
    status = Column(String(20), nullable=False, server_default=text("'active'"), default="active")
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    partner = relationship("Partner", backref="assignments")
    product = relationship("Product", backref="assignments")

    __table_args__ = (
        CheckConstraint("remaining_quantity >= 0", name="check_remaining_nonnegative"),
        CheckConstraint(
            "share_percentage >= 0 AND share_percentage <= 100",
            name="check_share_percentage_range",
        ),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "partner_id": str(self.partner_id),
            "product_id": str(self.product_id),
            "assigned_quantity": self.assigned_quantity,
            "remaining_quantity": self.remaining_quantity,
            "share_percentage": float(self.share_percentage)
            if self.share_percentage is not None
            else None,
            "status": self.status,
            "fulfilled_at": self.fulfilled_at.isoformat() if self.fulfilled_at else None,
        }
