from sqlalchemy import Column, String, Text, DateTime, text
from app.core.db_types import GUID
import uuid

from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text(), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
