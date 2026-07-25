from datetime import date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession


async def get_supplier_summary_report(
    db: AsyncSession,
) -> List[Dict[str, Any]]:
    from app.models.supplier import Supplier
    from app.models.supplier_ledger import SupplierLedger

    query = select(Supplier).order_by(Supplier.created_at.desc())
    result = await db.execute(query)
    suppliers = result.scalars().all()

    data = []
    for supplier in suppliers:
        purchases_query = select(
            func.coalesce(
                func.sum(
                    case(
                        (SupplierLedger.type == "PURCHASE", SupplierLedger.amount),
                        else_=0,
                    )
                ),
                Decimal(0),
            )
        ).where(SupplierLedger.supplier_id == supplier.id)
        result = await db.execute(purchases_query)
        total_purchases = result.scalar() or Decimal(0)

        payments_query = select(
            func.coalesce(
                func.sum(
                    case(
                        (SupplierLedger.type == "PAYMENT", SupplierLedger.amount),
                        else_=0,
                    )
                ),
                Decimal(0),
            )
        ).where(SupplierLedger.supplier_id == supplier.id)
        result = await db.execute(payments_query)
        total_payments = result.scalar() or Decimal(0)

        returns_query = select(
            func.coalesce(
                func.sum(
                    case(
                        (SupplierLedger.type == "RETURN", SupplierLedger.amount),
                        else_=0,
                    )
                ),
                Decimal(0),
            )
        ).where(SupplierLedger.supplier_id == supplier.id)
        result = await db.execute(returns_query)
        total_returns = result.scalar() or Decimal(0)

        balance = total_purchases - total_payments - total_returns

        data.append(
            {
                "id": str(supplier.id),
                "name": supplier.name,
                "total_purchases": total_purchases,
                "total_payments": total_payments,
                "total_returns": total_returns,
                "balance": balance,
            }
        )

    return data


async def get_supplier_statement(
    db: AsyncSession,
    supplier_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    from app.models.supplier import Supplier
    from app.models.supplier_ledger import SupplierLedger

    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise ValueError(f"Supplier {supplier_id} not found")

    purchases_query = select(
        func.coalesce(
            func.sum(
                case(
                    (SupplierLedger.type == "PURCHASE", SupplierLedger.amount),
                    else_=0,
                )
            ),
            Decimal(0),
        )
    ).where(SupplierLedger.supplier_id == supplier_id)
    result = await db.execute(purchases_query)
    total_purchases = result.scalar() or Decimal(0)

    payments_query = select(
        func.coalesce(
            func.sum(
                case(
                    (SupplierLedger.type == "PAYMENT", SupplierLedger.amount),
                    else_=0,
                )
            ),
            Decimal(0),
        )
    ).where(SupplierLedger.supplier_id == supplier_id)
    result = await db.execute(payments_query)
    total_payments = result.scalar() or Decimal(0)

    returns_query = select(
        func.coalesce(
            func.sum(
                case(
                    (SupplierLedger.type == "RETURN", SupplierLedger.amount),
                    else_=0,
                )
            ),
            Decimal(0),
        )
    ).where(SupplierLedger.supplier_id == supplier_id)
    result = await db.execute(returns_query)
    total_returns = result.scalar() or Decimal(0)

    balance = total_purchases - total_payments - total_returns

    ledger_query = (
        select(SupplierLedger)
        .where(SupplierLedger.supplier_id == supplier_id)
        .order_by(SupplierLedger.created_at.desc())
    )

    if start_date:
        ledger_query = ledger_query.where(SupplierLedger.created_at >= start_date)
    if end_date:
        ledger_query = ledger_query.where(SupplierLedger.created_at <= end_date)

    result = await db.execute(ledger_query)
    ledger_entries = result.scalars().all()

    return {
        "supplier": {
            "id": str(supplier.id),
            "name": supplier.name,
        },
        "summary": {
            "total_purchases": total_purchases,
            "total_payments": total_payments,
            "total_returns": total_returns,
            "balance": balance,
        },
        "ledger": [
            {
                "id": str(entry.id),
                "type": entry.type,
                "amount": entry.amount,
                "reference_id": str(entry.reference_id)
                if entry.reference_id
                else None,
                "note": entry.note,
                "created_at": entry.created_at,
            }
            for entry in ledger_entries
        ],
    }
