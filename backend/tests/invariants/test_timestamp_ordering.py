"""Timestamp ordering invariant tests.

Verifies that:
1. BaseModel created_at has func.now() Python-side default (microsecond precision for new rows)
2. Tie-breaking on Model.id provides deterministic ordering when timestamps match
"""

import uuid

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.sale import Sale


async def test_created_at_has_python_default(db_session: AsyncSession):
    """BaseModel.created_at must have a Python-side func.now() default for microsecond precision."""
    from app.core.database import BaseModel

    mapper = inspect(Product)
    col = mapper.columns.created_at

    assert col.server_default is not None, "created_at must have server_default"
    assert col.default is not None, (
        "created_at must have a Python-side default (func.now()). "
        "Without it, SQLite CURRENT_TIMESTAMP gives only second-level precision."
    )


async def test_tie_break_by_id_deterministic(db_session: AsyncSession):
    """When two rows share the same created_at second, order_by desc must be deterministic via id."""
    from app.models.payment_method import PaymentMethod

    pm = PaymentMethod(id=uuid.uuid4(), name="Cash")
    db_session.add(pm)
    await db_session.flush()

    now_str = "2026-01-01 12:00:00"

    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    s1 = Sale(
        id=id1,
        payment_method_id=pm.id,
        subtotal=100,
        grand_total=100,
    )
    s2 = Sale(
        id=id2,
        payment_method_id=pm.id,
        subtotal=200,
        grand_total=200,
    )
    db_session.add_all([s1, s2])
    await db_session.flush()

    # Override created_at to the same second to force tie
    await db_session.execute(
        text("UPDATE sales SET created_at = :ts WHERE id = :id").bindparams(ts=now_str, id=str(id1))
    )
    await db_session.execute(
        text("UPDATE sales SET created_at = :ts WHERE id = :id").bindparams(ts=now_str, id=str(id2))
    )

    query = (
        select(Sale)
        .where(Sale.id.in_([id1, id2]))
        .order_by(
            Sale.created_at.desc(),
            Sale.id.desc(),
        )
    )
    result = await db_session.execute(query)
    rows = list(result.scalars().all())

    assert len(rows) == 2

    if id2 > id1:
        assert rows[0].id == id2
        assert rows[1].id == id1
    else:
        assert rows[0].id == id1
        assert rows[1].id == id2
