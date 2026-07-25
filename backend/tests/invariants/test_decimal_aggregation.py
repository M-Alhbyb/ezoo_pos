"""
Money-guard test.

Proves that SQLite Numeric(12,2) round-trips through SUM aggregation
faithfully enough for a single-shop POS.  If this ever fails, the
integer-minor-units migration becomes necessary.
"""

import random
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, insert, select

from app.models.payment_method import PaymentMethod
from app.models.sale import Sale


async def _ensure_payment_method(session):
    """Create a throwaway payment method so Sale FKs are satisfied."""
    pm = PaymentMethod(name="Test PM", is_active=True)
    session.add(pm)
    await session.flush()
    return pm.id


async def test_sql_sum_matches_python_decimal_sum(db_session):
    """SUM of 50 000 Numeric(12,2) rows must match exact Decimal arithmetic."""
    pm_id = await _ensure_payment_method(db_session)

    random.seed(1)
    values = [Decimal(random.randrange(1, 10_000_00)) / 100 for _ in range(50_000)]

    rows = [
        {
            "payment_method_id": pm_id,
            "subtotal": v,
            "fees_total": Decimal("0"),
            "vat_total": Decimal("0"),
            "grand_total": v,
            "total_cost": Decimal("0"),
            "profit": Decimal("0"),
        }
        for v in values
    ]

    await db_session.execute(insert(Sale), rows)
    await db_session.flush()

    sql_total = (await db_session.execute(select(func.sum(Sale.grand_total)))).scalar()
    expected = sum(values)

    assert Decimal(str(sql_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == expected


async def test_round_trip_edge_cases(db_session):
    """Awkward cent values (.005, .015, .995) must survive a round trip."""
    pm_id = await _ensure_payment_method(db_session)

    edge_values = [
        Decimal("0.005"),
        Decimal("0.015"),
        Decimal("0.995"),
        Decimal("1.005"),
        Decimal("99.995"),
        Decimal("1234.565"),
        Decimal("0.04"),   # rounding down
        Decimal("0.05"),   # rounding up
    ]

    rows = [
        {
            "payment_method_id": pm_id,
            "subtotal": v,
            "fees_total": Decimal("0"),
            "vat_total": Decimal("0"),
            "grand_total": v,
            "total_cost": Decimal("0"),
            "profit": Decimal("0"),
        }
        for v in edge_values
    ]
    await db_session.execute(insert(Sale), rows)
    await db_session.flush()

    sql_total = (await db_session.execute(select(func.sum(Sale.grand_total)))).scalar()
    expected = sum(edge_values)

    assert Decimal(str(sql_total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == expected


async def test_numeric_rate_columns_round_trip(db_session):
    """Numeric(5,2) rate columns (vat_rate, share_percentage) round-trip exactly."""
    pm_id = await _ensure_payment_method(db_session)

    rate_values = [
        Decimal("16.00"),
        Decimal("5.50"),
        Decimal("0.05"),
        Decimal("99.99"),
        Decimal("12.34"),
    ]

    for v in rate_values:
        row = Sale(
            payment_method_id=pm_id,
            subtotal=Decimal("0"),
            fees_total=Decimal("0"),
            vat_rate=v,
            vat_total=Decimal("0"),
            grand_total=Decimal("0"),
            total_cost=Decimal("0"),
            profit=Decimal("0"),
        )
        db_session.add(row)
    await db_session.flush()

    result = await db_session.execute(select(Sale.vat_rate).where(Sale.vat_rate.isnot(None)))
    stored = {row[0] for row in result.all()}

    for v in rate_values:
        assert v in stored, f"Numeric(5,2) value {v} not found after round-trip"
