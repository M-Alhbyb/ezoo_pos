from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Numeric, String, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.product import Product


class ProjectItem(Base):
    __tablename__ = "project_items"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Snapshot
    base_cost = Column(Numeric(12, 2), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    project = relationship("Project", back_populates="items")
    product = relationship("Product", foreign_keys=[product_id])
