from decimal import Decimal
from sqlalchemy import Column, String, Numeric, DateTime, text
from app.core.db_types import GUID
from sqlalchemy import Integer

from app.core.database import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String(200), nullable=False)
    investment_amount = Column(Numeric(12, 2), nullable=False, default=0, server_default='0')
    share_percentage = Column(Numeric(5, 2), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
