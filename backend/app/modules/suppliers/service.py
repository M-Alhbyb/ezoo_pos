from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.models.supplier_ledger import SupplierLedger
from app.schemas.supplier import SupplierCreate, SupplierSummary


class SupplierService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_supplier(self, data: SupplierCreate) -> Supplier:
        supplier = Supplier(
            name=data.name,
            phone=data.phone,
            notes=data.notes,
        )
        self.db.add(supplier)
        await self.db.commit()
        await self.db.refresh(supplier)
        return supplier

    async def get_suppliers(self) -> List[Supplier]:
        query = select(Supplier).order_by(Supplier.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_supplier(self, supplier_id: UUID) -> Optional[Supplier]:
        query = select(Supplier).where(Supplier.id == supplier_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_supplier_balance(self, supplier_id: UUID) -> Decimal:
        query = select(
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

        result = await self.db.execute(query)
        total_purchases = result.scalar() or Decimal(0)

        query = select(
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

        result = await self.db.execute(query)
        total_payments = result.scalar() or Decimal(0)

        query = select(
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

        result = await self.db.execute(query)
        total_returns = result.scalar() or Decimal(0)

        return total_purchases - total_payments - total_returns

    async def get_supplier_summary(self, supplier_id: UUID) -> SupplierSummary:
        query = select(
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

        result = await self.db.execute(query)
        total_purchases = result.scalar() or Decimal(0)

        query = select(
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

        result = await self.db.execute(query)
        total_payments = result.scalar() or Decimal(0)

        query = select(
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

        result = await self.db.execute(query)
        total_returns = result.scalar() or Decimal(0)

        balance = total_purchases - total_payments - total_returns

        return SupplierSummary(
            total_purchases=total_purchases,
            total_payments=total_payments,
            total_returns=total_returns,
            balance=balance,
        )

    async def record_payment(
        self,
        supplier_id: UUID,
        amount: Decimal,
        note: Optional[str] = None,
    ) -> SupplierLedger:
        ledger = SupplierLedger(
            supplier_id=supplier_id,
            type="PAYMENT",
            amount=amount,
            note=note,
        )
        self.db.add(ledger)
        await self.db.commit()
        await self.db.refresh(ledger)
        return ledger
