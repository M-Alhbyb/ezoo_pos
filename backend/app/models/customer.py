from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import String, Text, Numeric, ForeignKey, DateTime, func, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.constants import LedgerTransactionType


class Customer(Base):
    """
    Represents a credit-eligible customer.
    """
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0.00", nullable=False)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    ledger_entries: Mapped[List["CustomerLedger"]] = relationship(
        "CustomerLedger", back_populates="customer", cascade="all, delete-orphan"
    )
    sales: Mapped[List["Sale"]] = relationship("Sale", back_populates="customer")


class CustomerLedger(Base):
    """
    Append-only log of all financial interactions.
    """
    __tablename__ = "customer_ledger"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="ledger_entries")


# T010.5 Immutability Enforcement
@event.listens_for(CustomerLedger, "before_update")
def block_ledger_update(mapper, connection, target):
    raise RuntimeError("CustomerLedger entries are immutable and cannot be updated.")


@event.listens_for(CustomerLedger, "before_delete")
def block_ledger_delete(mapper, connection, target):
    raise RuntimeError("CustomerLedger entries are immutable and cannot be deleted.")
