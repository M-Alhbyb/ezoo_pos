from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, text
from app.core.db_types import GUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SupplierLedger(Base):
    __tablename__ = "supplier_ledger"

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
    type = Column(String(20), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    reference_id = Column(GUID(), nullable=True)
    note = Column(Text(), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    supplier = relationship("Supplier", backref="ledger_entries")
