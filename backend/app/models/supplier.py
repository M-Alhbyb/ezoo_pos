from sqlalchemy import Column, String, Text, DateTime, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text(), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
