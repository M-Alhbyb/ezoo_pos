import os
import uuid

from sqlalchemy import Column, DateTime, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.core.db_types import GUID

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


def _install_pragmas(sync_engine) -> None:
    @event.listens_for(sync_engine, "connect")
    def _set_pragmas(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.close()


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
        _install_pragmas(_async_engine.sync_engine)
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
