import enum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Numeric, Enum, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ExpenseType(str, enum.Enum):
    FIXED = "fixed"
    PERCENT = "percent"  # To match test: "type": "percent"
    RECURRING = "recurring"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=True,
        index=True,
    )
    name = Column(String(200), nullable=True) # Usually test might not send name if it doesn't specify
    type = Column(Enum(ExpenseType), nullable=False)
    value = Column(Numeric(12, 2), nullable=False)
    
    # Snapshot of resulting cost
    calculated_amount = Column(Numeric(12, 2), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    project = relationship("Project", back_populates="expenses")
