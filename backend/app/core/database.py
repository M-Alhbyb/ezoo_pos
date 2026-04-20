from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.config import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Extensibility columns for future multi-user/multi-branch support
    user_id = Column(UUID(as_uuid=True), nullable=True)
    branch_id = Column(UUID(as_uuid=True), nullable=True)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
