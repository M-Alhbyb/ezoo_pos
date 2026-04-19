from decimal import Decimal
from sqlalchemy import Column, Numeric, DateTime, text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class PartnerDistribution(Base):
    __tablename__ = "partner_distributions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    partner_id = Column(
        Integer,
        ForeignKey("partners.id"),
        nullable=False,
        index=True,
    )
    payout_amount = Column(Numeric(12, 2), nullable=False)
    snapshot_fields = Column(JSONB, nullable=False, server_default='{}')

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
