from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String(200), nullable=False)
    investment_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default='0')
    share_percentage = Column(Numeric(5, 2), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
