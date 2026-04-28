"""
Partner Wallet Transaction Model - Immutable record of all wallet balance changes.

Constitution compliance:
- IV (Immutable Financial Records): Never updated or deleted after creation
- I (Financial Accuracy): DECIMAL for monetary values, traceable to sale_id
- VI (Data Integrity): created_at timestamp, amount CHECK constraint
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
import uuid

from sqlalchemy import (
    Column,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint,
    Index,
    text,
    Integer,
)
from app.core.db_types import GUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PartnerWalletTransaction(Base):
    """
    Immutable record of all wallet balance changes for audit trail.

    Every change to a partner's wallet balance is recorded here:
    - sale_profit: Credit from selling assigned products
    - manual_adjustment: Admin-initiated credit or debit

    Each transaction stores balance_after, enabling O(1) balance lookup
    without summing all historical transactions.

    Business Rules:
    - Immutable after creation (no UPDATE or DELETE operations)
    - amount cannot be 0 (CHECK constraint)
    - balance_after computed as previous balance + amount
    - reference_id links to sale_id for sale_profit transactions
    """

    __tablename__ = "partner_wallet_transactions"

    # Primary key
    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign keys
    partner_id = Column(
        Integer,
        ForeignKey("partners.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Partner whose wallet changed",
    )

    # Core fields
    amount = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Credit (positive) or debit (negative)",
    )

    transaction_type = Column(
        String(50),
        nullable=False,
        comment="'sale_profit' or 'manual_adjustment'",
    )

    reference_id = Column(
        GUID(),
        nullable=True,
        comment="FK to sale_id or NULL for manual",
    )

    reference_type = Column(
        String(50),
        nullable=True,
        comment="'sale' or 'manual'",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Human-readable description",
    )

    balance_after = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Wallet balance after this transaction",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Transaction timestamp",
    )

    # Extensibility (for future multi-user support)
    created_by = Column(
        GUID(),
        nullable=True,
        comment="User who initiated transaction",
    )

    # Relationships
    partner = relationship("Partner", backref="wallet_transactions")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "amount != 0",
            name="check_amount_nonzero",
        ),
        Index(
            "idx_partner_transactions",
            "partner_id",
            "created_at",
        ),
    )

    def __repr__(self):
        return f"<PartnerWalletTransaction {self.id} - Partner: {self.partner_id}, Amount: {self.amount}, Balance After: {self.balance_after}>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "partner_id": self.partner_id,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type,
            "reference_id": str(self.reference_id) if self.reference_id else None,
            "reference_type": self.reference_type,
            "description": self.description,
            "balance_after": float(self.balance_after),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
