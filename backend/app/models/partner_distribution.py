from decimal import Decimal
from sqlalchemy import Column, Numeric, DateTime, text, ForeignKey, Integer, Text
from app.core.db_types import GUID
import uuid

from app.core.database import Base


class PartnerDistribution(Base):
    __tablename__ = "partner_distributions"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    partner_id = Column(
        Integer,
        ForeignKey("partners.id"),
        nullable=False,
        index=True,
    )
    payout_amount = Column(Numeric(12, 2), nullable=False)
    snapshot_fields = Column(Text, nullable=False, server_default='{}')

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
