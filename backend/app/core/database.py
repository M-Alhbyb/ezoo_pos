from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, text, create_engine
from sqlalchemy.pool import StaticPool
from app.core.db_types import GUID
import uuid
import os

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    created_at = Column(
        DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=text('CURRENT_TIMESTAMP'),
        nullable=False,
    )

    user_id = Column(GUID(), nullable=True)
    branch_id = Column(GUID(), nullable=True)


def get_database_url():
    database_path = os.environ.get('DATABASE_PATH', 'ezoo_pos.db')
    return f'sqlite+aiosqlite:///{database_path}'


def get_sync_database_url():
    database_path = os.environ.get('DATABASE_PATH', 'ezoo_pos.db')
    return f'sqlite:///{database_path}'


_async_engine = None
_async_session_local = None


def get_engine():
    global _async_engine
    if _async_engine is None:
        database_url = get_database_url()
        _async_engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            poolclass=StaticPool,
            connect_args={'check_same_thread': False},
        )
    return _async_engine


def get_session_maker():
    global _async_session_local
    if _async_session_local is None:
        engine = get_engine()
        _async_session_local = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_local


async def get_db() -> AsyncSession:
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db():
    sync_url = get_sync_database_url()
    engine = create_engine(sync_url, echo=False, connect_args={'check_same_thread': False})
    Base.metadata.create_all(bind=engine)
    seed_data(engine)
    engine.dispose()


def seed_data(engine):
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM payment_methods'))
        count = result.scalar()

        if count == 0:
            conn.execute(text('''
                INSERT INTO payment_methods (id, name, is_active, created_at, updated_at)
                VALUES
                    (lower(hex(randomblob(16))), 'Cash', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                    (lower(hex(randomblob(16))), 'M-PESA', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
                    (lower(hex(randomblob(16))), 'Card', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            '''))
            conn.commit()