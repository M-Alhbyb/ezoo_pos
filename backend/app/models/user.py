"""
User SQLAlchemy model.

Defines the User entity for authentication and authorization.
"""

from sqlalchemy import Column, String, Boolean
from app.core.database import BaseModel


class User(BaseModel):
    """
    User model for authentication.

    Phase 6 — JWT-based auth for single-operator POS.
    """

    __tablename__ = "users"

    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="operator")  # admin | operator
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
