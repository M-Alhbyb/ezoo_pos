from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class SupplierLedger(Base):
    __tablename__ = "supplier_ledger"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    supplier_id = Column(
        UUID(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    note = Column(Text(), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    supplier = relationship("Supplier", backref="ledger_entries")
