from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, cast, Date, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.partner_distribution import PartnerDistribution
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.models.partner import Partner
from app.models.sale_payment import SalePayment
from app.models.inventory_log import InventoryLog
from app.models.product import Product
from app.schemas.report import (
    SalesReport,
    SalesSummaryGroup,
    PartnerReport,
    PartnerPayoutSummary,
    InventoryReport,
    InventoryMovement,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales_count(self, start_date: date, end_date: date) -> int:
        """
        Count total sales records in date range for export validation.
        """
        stmt = select(func.count(Sale.id))
        if start_date:
            stmt = stmt.where(cast(Sale.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(Sale.created_at, Date) <= end_date)

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0

    async def get_partners_count(self, start_date: date, end_date: date) -> int:
        """
        Count total partner profit transactions in date range for export validation.
        """
        stmt = select(func.count(PartnerWalletTransaction.id)).where(
            PartnerWalletTransaction.transaction_type == "sale_profit"
        )
        if start_date:
            stmt = stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) >= start_date
            )
        if end_date:
            stmt = stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) <= end_date
            )

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0

    async def get_inventory_count(self, start_date: date, end_date: date) -> int:
        """
        Count total inventory movements in date range for export validation.
        """
        stmt = select(func.count(InventoryLog.id))
        if start_date:
            stmt = stmt.where(cast(InventoryLog.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(InventoryLog.created_at, Date) <= end_date)

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0

    async def get_sales_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        page: int = 1,
        page_size: int = 50,
    ) -> SalesReport:
        """
        Aggregate sales statistics with daily breakdown.
        """
        stmt = select(Sale)
        if start_date:
            stmt = stmt.where(cast(Sale.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(Sale.created_at, Date) <= end_date)

        # Totals for summary cards (not paginated)
        total_stmt = select(
            func.sum(Sale.grand_total).label("revenue"),
            func.sum(Sale.total_cost).label("cost"),
            func.sum(Sale.profit).label("profit"),
            func.count(Sale.id).label("count"),
        )
        if start_date:
            total_stmt = total_stmt.where(cast(Sale.created_at, Date) >= start_date)
        if end_date:
            total_stmt = total_stmt.where(cast(Sale.created_at, Date) <= end_date)

        total_result = await self.db.execute(total_stmt)
        total_row = total_result.one()

        # Daily breakdown via SQL aggregation for efficiency (Paginated)
        group_stmt = (
            select(
                cast(Sale.created_at, Date).label("day"),
                func.count(Sale.id).label("count"),
                func.sum(Sale.grand_total).label("revenue"),
                func.sum(Sale.total_cost).label("cost"),
                func.sum(Sale.profit).label("profit"),
            )
            .group_by("day")
            .order_by("day")
        )
        if start_date:
            group_stmt = group_stmt.where(cast(Sale.created_at, Date) >= start_date)
        if end_date:
            group_stmt = group_stmt.where(cast(Sale.created_at, Date) <= end_date)

        # Get total count of groups for pagination
        count_stmt = select(func.count()).select_from(group_stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_groups = count_result.scalar() or 0

        # Apply pagination
        group_stmt = group_stmt.limit(page_size).offset((page - 1) * page_size)

        group_result = await self.db.execute(group_stmt)
        daily_breakdown = [
            SalesSummaryGroup(
                date=row.day,
                count=row.count,
                revenue=row.revenue or Decimal("0.00"),
                cost=row.cost or Decimal("0.00"),
                profit=row.profit or Decimal("0.00"),
            )
            for row in group_result
        ]

        # Calculate total partner payouts for net profit calculation
        payout_stmt = select(func.sum(PartnerWalletTransaction.amount)).where(
            PartnerWalletTransaction.transaction_type == "sale_profit"
        )
        if start_date:
            payout_stmt = payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) >= start_date
            )
        if end_date:
            payout_stmt = payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) <= end_date
            )

        payout_res = await self.db.execute(payout_stmt)
        total_partner_profit = payout_res.scalar() or Decimal("0.00")

        gross_profit = total_row.profit or Decimal("0.00")
        total_net_profit = gross_profit - total_partner_profit

        return SalesReport(
            total_revenue=total_row.revenue or Decimal("0.00"),
            total_cost=total_row.cost or Decimal("0.00"),
            total_profit=gross_profit,
            total_partner_profit=total_partner_profit,
            total_net_profit=total_net_profit,
            sales_count=total_row.count or 0,
            daily_breakdown=daily_breakdown,
            total=total_groups,
            page=page,
            page_size=page_size,
        )

    async def get_partners_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        page: int = 1,
        page_size: int = 50,
    ) -> PartnerReport:
        """
        Aggregate partner distributions grouped by partner.
        """
        payout_stmt = (
            select(
                Partner.id.label("partner_id"),
                Partner.name.label("partner_name"),
                func.sum(PartnerWalletTransaction.amount).label("total_payout"),
            )
            .join(Partner, Partner.id == PartnerWalletTransaction.partner_id)
            .where(PartnerWalletTransaction.transaction_type == "sale_profit")
            .group_by(Partner.id, Partner.name)
        )

        if start_date:
            payout_stmt = payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) >= start_date
            )
        if end_date:
            payout_stmt = payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) <= end_date
            )

        # Get total for pagination
        count_stmt = select(func.count()).select_from(payout_stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Apply pagination
        payout_stmt = payout_stmt.limit(page_size).offset((page - 1) * page_size)

        result = await self.db.execute(payout_stmt)
        payouts_by_partner = [
            PartnerPayoutSummary(
                partner_id=row.partner_id,
                partner_name=row.partner_name,
                total_payout=row.total_payout or Decimal("0.00"),
            )
            for row in result
        ]

        # Overall total payout (not paginated)
        total_payout_stmt = select(func.sum(PartnerWalletTransaction.amount)).where(
            PartnerWalletTransaction.transaction_type == "sale_profit"
        )
        if start_date:
            total_payout_stmt = total_payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) >= start_date
            )
        if end_date:
            total_payout_stmt = total_payout_stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) <= end_date
            )

        total_payout_res = await self.db.execute(total_payout_stmt)
        overall_total_payout = total_payout_res.scalar() or Decimal("0.00")

        return PartnerReport(
            total_payout=overall_total_payout,
            payouts_by_partner=payouts_by_partner,
            total=total_count,
            page=page,
            page_size=page_size,
        )

    async def get_inventory_report(
        self,
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
            stmt = stmt.where(cast(InventoryLog.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(InventoryLog.created_at, Date) <= end_date)

        # Get total for pagination
        count_stmt = select(func.count()).select_from(stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Apply pagination
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)

        result = await self.db.execute(stmt)
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
                cast(InventoryLog.created_at, Date) >= start_date
            )
        if end_date:
            total_mov_stmt = total_mov_stmt.where(
                cast(InventoryLog.created_at, Date) <= end_date
            )
        total_mov_res = await self.db.execute(total_mov_stmt)
        overall_total_movements = total_mov_res.scalar() or 0

        return InventoryReport(
            total_movements=overall_total_movements,
            movements_by_reason=movements,
            total=total_count,
            page=page,
            page_size=page_size,
        )

    async def get_sales_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        # Load sales with payments and their associated method names
        stmt = (
            select(Sale)
            .options(
                selectinload(Sale.payments).selectinload(SalePayment.payment_method)
            )
            .order_by(Sale.created_at.desc())
        )
        if start_date:
            stmt = stmt.where(cast(Sale.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(Sale.created_at, Date) <= end_date)

        result = await self.db.execute(stmt)
        sales = result.scalars().all()

        # Fetch partner payouts for these sales
        # Map sale_id -> sum(amount)
        sale_ids = [sale.id for sale in sales]
        payouts_by_sale = {}
        if sale_ids:
            payout_stmt = (
                select(
                    PartnerWalletTransaction.reference_id,
                    func.sum(PartnerWalletTransaction.amount),
                )
                .where(PartnerWalletTransaction.reference_id.in_(sale_ids))
                .where(PartnerWalletTransaction.transaction_type == "sale_profit")
                .group_by(PartnerWalletTransaction.reference_id)
            )
            payout_res = await self.db.execute(payout_stmt)
            for row in payout_res:
                payouts_by_sale[row[0]] = row[1]

        data = []
        for sale in sales:
            partner_share = payouts_by_sale.get(sale.id, Decimal("0.00"))
            gross_profit = sale.profit or Decimal("0.00")
            net_profit = gross_profit - partner_share

            # Combine payment methods into a string
            methods = (
                ", ".join([p.payment_method_name for p in sale.payments])
                if sale.payments
                else ""
            )

            data.append(
                {
                    "Date": str(sale.created_at),
                    "Payment Methods": methods,
                    "Subtotal": sale.subtotal,
                    "Fees": sale.fees_total,
                    "VAT": sale.vat_total,
                    "Grand Total": sale.grand_total,
                    "Gross Profit": gross_profit,
                    "Partner Share": partner_share,
                    "Net Profit": net_profit,
                    "Note": sale.note or "",
                }
            )
        return data

    async def get_partners_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(
                PartnerWalletTransaction,
                Partner.name.label("partner_name"),
                Partner.investment_amount.label("invested_amount"),
                Partner.share_percentage.label("profit_percentage"),
            )
            .join(Partner, Partner.id == PartnerWalletTransaction.partner_id)
            .where(PartnerWalletTransaction.transaction_type == "sale_profit")
            .order_by(PartnerWalletTransaction.created_at.desc())
        )
        if start_date:
            stmt = stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) >= start_date
            )
        if end_date:
            stmt = stmt.where(
                cast(PartnerWalletTransaction.created_at, Date) <= end_date
            )

        result = await self.db.execute(stmt)
        data = []
        for row in result:
            trans = row.PartnerWalletTransaction
            data.append(
                {
                    "name": row.partner_name,
                    "invested_amount": row.invested_amount,
                    "profit_percentage": row.profit_percentage,
                    "distributed_amount": trans.amount,
                    "distribution_date": str(trans.created_at),
                }
            )
        return data

    async def get_inventory_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        stmt = (
            select(InventoryLog, Product.name.label("product_name"))
            .join(Product, Product.id == InventoryLog.product_id)
            .order_by(InventoryLog.created_at.desc())
        )
        if start_date:
            stmt = stmt.where(cast(InventoryLog.created_at, Date) >= start_date)
        if end_date:
            stmt = stmt.where(cast(InventoryLog.created_at, Date) <= end_date)

        result = await self.db.execute(stmt)
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

    async def get_supplier_summary_report(
        self,
    ) -> List[Dict[str, Any]]:
        from app.models.supplier import Supplier
        from app.models.supplier_ledger import SupplierLedger

        query = select(Supplier).order_by(Supplier.created_at.desc())
        result = await self.db.execute(query)
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
            result = await self.db.execute(purchases_query)
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
            result = await self.db.execute(payments_query)
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
            result = await self.db.execute(returns_query)
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
        self,
        supplier_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        from app.models.supplier import Supplier
        from app.models.supplier_ledger import SupplierLedger

        supplier = await self.db.get(Supplier, supplier_id)
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
        result = await self.db.execute(purchases_query)
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
        result = await self.db.execute(payments_query)
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
        result = await self.db.execute(returns_query)
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

        result = await self.db.execute(ledger_query)
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
