"""
Pytest configuration for EZOO POS backend tests.

This conftest.py provides:
- Database fixtures for testing
- Test client fixtures
- Common test utilities
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import pool
from sqlalchemy.orm import declarative_base

from app.core.database import Base, get_db
from main import app


# Test database URL (use PostgreSQL test database)
TEST_DATABASE_URL = "postgresql+asyncpg://pasha:pshpsh00@localhost:5432/ezoo_pos_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def async_client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with isolated DB sessions per request."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    async_session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def override_get_db():
        async with async_session_maker() as session:
            yield session
            await session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def client(async_client):
    """Alias for async_client fixture."""
    yield async_client


# Test utilities
@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
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
    """Sample sale data for testing."""
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
