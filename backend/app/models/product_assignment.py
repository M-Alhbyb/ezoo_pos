"""
Product Assignment Model - Links products to partners for profit sharing.

Constitution compliance:
- VI (Data Integrity): DECIMAL for monetary, timestamps on all records
- IV (Immutable Financial Records): Assignment fulfillment tracked via status
- IX (Extensibility): created_by, branch_id for future multi-user/multi-branch
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductAssignment(Base):
    """
    Assigns specific product quantities to partners for profit sharing.

    Tracks how many units of a product are allocated to each partner,
    with remaining_quantity decreasing as sales occur.

    State transitions:
    - NEW: assigned_quantity set, remaining_quantity = assigned_quantity, status='active'
    - SALE: remaining_quantity -= quantity_sold
    - FULFILLED: remaining_quantity == 0, status='fulfilled', fulfilled_at set

    Business Rules:
    - Only one active assignment per product (enforced at application layer)
    - remaining_quantity never goes below 0 (CHECK constraint)
    - share_percentage defaults to partner's share_percentage if not specified
    - Cannot delete partner or product with existing assignments (RESTRICT FK)
    """

    __tablename__ = "product_assignments"

    # Primary key
    id = Column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Foreign keys
    partner_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("partners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Partner receiving profit share",
    )

    product_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Product assigned to partner",
    )

    # Core fields
    assigned_quantity = Column(
        Integer,
        nullable=False,
        comment="Original quantity assigned",
    )

    remaining_quantity = Column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Quantity remaining unsold",
    )

    share_percentage = Column(
        Numeric(5, 2),
        nullable=False,
        comment="Profit share (overrides partner default)",
    )

    status = Column(
        String(20),
        nullable=False,
        server_default="active",
        default="active",
        comment="'active' or 'fulfilled'",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        comment="Creation timestamp",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp",
    )

    fulfilled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When remaining_quantity hit 0",
    )

    # Extensibility (for future multi-user/multi-branch)
    created_by = Column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="User who created assignment",
    )

    branch_id = Column(
        PG_UUID(as_uuid=True),
        nullable=True,
        comment="Branch for multi-branch support",
    )

    # Relationships
    partner = relationship("Partner", backref="assignments")
    product = relationship("Product", backref="assignments")

    def __init__(self, **kwargs):
        """Initialize ProductAssignment with defaults."""
        if "status" not in kwargs:
            kwargs["status"] = "active"
        super().__init__(**kwargs)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "remaining_quantity >= 0",
            name="check_remaining_nonnegative",
        ),
        CheckConstraint(
            "share_percentage >= 0 AND share_percentage <= 100",
            name="check_share_percentage_range",
        ),
        Index(
            "idx_product_assignment_active",
            "product_id",
            "status",
            "remaining_quantity",
        ),
        Index("idx_partner_assignments", "partner_id"),
    )

    def __repr__(self):
        return f"<ProductAssignment {self.id} - Product: {self.product_id}, Partner: {self.partner_id}, Remaining: {self.remaining_quantity}/{self.assigned_quantity}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "partner_id": str(self.partner_id),
            "product_id": str(self.product_id),
            "assigned_quantity": self.assigned_quantity,
            "remaining_quantity": self.remaining_quantity,
            "share_percentage": float(self.share_percentage),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "fulfilled_at": self.fulfilled_at.isoformat()
            if self.fulfilled_at
            else None,
        }
