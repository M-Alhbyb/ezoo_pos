"""
Pytest configuration for EZOO POS backend tests.

Uses per-test temp-file SQLite databases so the suite runs with zero
external services.  Module-level singletons in database.py are reset
between tests so each test gets an isolated database.
"""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from main import app


def _install_pragmas(sync_engine) -> None:
    @event.listens_for(sync_engine, "connect")
    def _set_pragmas(dbapi_conn, _record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.close()


@pytest_asyncio.fixture
async def engine(tmp_path):
    """Create a fresh SQLite engine per test, backed by a temp file."""
    db_path = str(tmp_path / "test_ezoo.db")
    os.environ["DATABASE_PATH"] = db_path

    import app.core.database as db_mod
    db_mod._async_engine = None
    db_mod._async_session_local = None

    eng = create_async_engine(
        f"sqlite+aiosqlite:///{db_path}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
    )
    _install_pragmas(eng.sync_engine)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async session bound to the per-test database."""
    maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def db(db_session) -> AsyncGenerator[AsyncSession, None]:
    """Alias used by unit / integration tests that request ``db``."""
    yield db_session


@pytest_asyncio.fixture
async def async_client(engine) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client wired to the per-test database."""
    maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def override_get_db():
        async with maker() as session:
            yield session
            await session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def client(async_client):
    """Alias for async_client fixture."""
    yield async_client


# ---------------------------------------------------------------------------
# Shared sample data
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_product_data():
    return {
        "name": "Test Product",
        "sku": "TEST-001",
        "category_id": "test-category-id",
        "base_price": "100.00",
        "selling_price": "150.00",
        "stock_quantity": 50,
    }


@pytest.fixture
def sample_sale_data():
    return {
        "items": [
            {"product_id": "test-product-id", "quantity": 2, "unit_price": "150.00"}
        ],
        "fees": [
            {
                "fee_type": "shipping",
                "fee_label": "Standard Shipping",
                "fee_value_type": "fixed",
                "fee_value": "30.00",
            }
        ],
        "payment_method_id": "test-payment-method-id",
    }
