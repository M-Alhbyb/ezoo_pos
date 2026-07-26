from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_log import InventoryLog
from app.models.product import Product
from app.schemas.report import (
    InventoryReport,
    InventoryMovement,
)


async def get_inventory_count(db: AsyncSession, start_date: date, end_date: date) -> int:
    """
    Count total inventory movements in date range for export validation.
    """
    stmt = select(func.count(InventoryLog.id))
    if start_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) <= end_date)

    result = await db.execute(stmt)
    count = result.scalar()
    return count or 0


async def get_inventory_report(
    db: AsyncSession,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    page: int = 1,
    page_size: int = 50,
) -> InventoryReport:
    """
    Aggregate inventory movements by reason.
    """
    stmt = select(
        InventoryLog.reason,
        func.sum(InventoryLog.delta).label("total_delta"),
        func.count(InventoryLog.id).label("movement_count"),
    ).group_by(InventoryLog.reason)

    if start_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) <= end_date)

    # Get total for pagination
    count_stmt = select(func.count()).select_from(stmt.alias("subquery"))
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # Apply pagination
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    result = await db.execute(stmt)
    movements = []
    total_delta_count = 0

    for row in result:
        total_delta_count += row.movement_count
        movements.append(
            InventoryMovement(
                reason=row.reason,
                total_delta=int(row.total_delta) if row.total_delta else 0,
            )
        )

    # Get total movements count (not paginated)
    total_mov_stmt = select(func.count(InventoryLog.id))
    if start_date:
        total_mov_stmt = total_mov_stmt.where(
            func.date(InventoryLog.created_at) >= start_date
        )
    if end_date:
        total_mov_stmt = total_mov_stmt.where(
            func.date(InventoryLog.created_at) <= end_date
        )
    total_mov_res = await db.execute(total_mov_stmt)
    overall_total_movements = total_mov_res.scalar() or 0

    return InventoryReport(
        total_movements=overall_total_movements,
        movements_by_reason=movements,
        total=total_count,
        page=page,
        page_size=page_size,
    )


async def get_inventory_export_data(
    db: AsyncSession, start_date: Optional[date], end_date: Optional[date]
) -> List[Dict[str, Any]]:
    stmt = (
        select(InventoryLog, Product.name.label("product_name"))
        .join(Product, Product.id == InventoryLog.product_id)
        .order_by(InventoryLog.created_at.desc(), InventoryLog.id.desc())
    )
    if start_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(InventoryLog.created_at) <= end_date)

    result = await db.execute(stmt)
    data = []
    for row in result:
        log = row.InventoryLog
        movement_type = (
            "داخل" if log.delta > 0 else ("خارج" if log.delta < 0 else "لا شيء")
        )
        data.append(
            {
                "product_name": row.product_name,
                "movement_type": movement_type,
                "quantity_delta": log.delta,
                "reason": log.reason,
                "created_at": str(log.created_at),
            }
        )
    return data
