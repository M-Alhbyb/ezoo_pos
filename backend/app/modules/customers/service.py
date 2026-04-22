from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date

from sqlalchemy import select, func, case, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer, CustomerLedger
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerSummary,
    CustomerListItem,
)
from app.core.constants import LedgerTransactionType


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_customer(self, data: CustomerCreate) -> Customer:
        """Create a new customer."""
        customer = Customer(
            name=data.name,
            phone=data.phone,
            address=data.address,
            notes=data.notes,
            credit_limit=data.credit_limit,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        """Get customer by ID."""
        query = select(Customer).where(Customer.id == customer_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_customers(self, page: int = 1, page_size: int = 50) -> Tuple[List[CustomerListItem], int]:
        """List customers with their derived balances."""
        # Derived balance subquery
        balance_sub = (
            select(
                CustomerLedger.customer_id,
                func.coalesce(
                    func.sum(
                        case(
                            (CustomerLedger.type == LedgerTransactionType.SALE, CustomerLedger.amount),
                            (CustomerLedger.type == LedgerTransactionType.PAYMENT, -CustomerLedger.amount),
                            (CustomerLedger.type == LedgerTransactionType.RETURN, -CustomerLedger.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("balance")
            )
            .group_by(CustomerLedger.customer_id)
            .subquery()
        )

        # Main query joining with subquery
        query = (
            select(
                Customer.id,
                Customer.name,
                Customer.phone,
                func.coalesce(balance_sub.c.balance, 0).label("balance"),
                Customer.credit_limit
            )
            .outerjoin(balance_sub, Customer.id == balance_sub.c.customer_id)
            .order_by(Customer.name)
        )

        # Count total
        count_query = select(func.count()).select_from(Customer)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        rows = result.all()

        customers = [
            CustomerListItem(
                id=row.id,
                name=row.name,
                phone=row.phone,
                balance=Decimal(row.balance),
                credit_limit=row.credit_limit,
            )
            for row in rows
        ]

        return customers, total

    async def get_customer_summary(self, customer_id: UUID) -> CustomerSummary:
        """Calculate dynamic summary for a customer."""
        query = select(
            func.coalesce(
                func.sum(
                    case(
                        (CustomerLedger.type == LedgerTransactionType.SALE, CustomerLedger.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_sales"),
            func.coalesce(
                func.sum(
                    case(
                        (CustomerLedger.type == LedgerTransactionType.PAYMENT, CustomerLedger.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_payments"),
            func.coalesce(
                func.sum(
                    case(
                        (CustomerLedger.type == LedgerTransactionType.RETURN, CustomerLedger.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_returns"),
        ).where(CustomerLedger.customer_id == customer_id)

        result = await self.db.execute(query)
        row = result.one()

        total_sales = Decimal(row.total_sales)
        total_payments = Decimal(row.total_payments)
        total_returns = Decimal(row.total_returns)
        balance = total_sales - total_payments - total_returns

        return CustomerSummary(
            total_sales=total_sales,
            total_payments=total_payments,
            total_returns=total_returns,
            balance=balance,
        )

    async def get_customer_balance(self, customer_id: UUID) -> Decimal:
        """Get current balance for a customer."""
        summary = await self.get_customer_summary(customer_id)
        return summary.balance

    async def check_credit_limit(self, customer_id: UUID, additional_debt: Decimal) -> Tuple[bool, Decimal, Decimal]:
        """
        Check if additional debt exceeds credit limit.
        Returns: (is_exceeded, current_balance, credit_limit)
        """
        customer = await self.get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        balance = await self.get_customer_balance(customer_id)
        is_exceeded = (balance + additional_debt) > customer.credit_limit
        
        return is_exceeded, balance, customer.credit_limit

    async def record_ledger_entry(
        self,
        customer_id: UUID,
        type: LedgerTransactionType,
        amount: Decimal,
        reference_id: Optional[UUID] = None,
        payment_method: Optional[str] = None,
        note: Optional[str] = None,
    ) -> CustomerLedger:
        """Create an immutable ledger entry."""
        entry = CustomerLedger(
            customer_id=customer_id,
            type=type,
            amount=amount,
            reference_id=reference_id,
            payment_method=payment_method,
            note=note,
        )
        self.db.add(entry)
        return entry

    async def record_payment(
        self,
        customer_id: UUID,
        amount: Decimal,
        payment_method: str,
        note: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> CustomerLedger:
        """
        Record a customer payment with idempotency support.
        T019.5: Prevents duplicate payment entries.
        """
        from sqlalchemy import select
        from app.models.customer import CustomerLedger

        if idempotency_key:
            existing_query = select(CustomerLedger).where(
                CustomerLedger.note == idempotency_key
            )
            result = await self.db.execute(existing_query)
            existing = result.scalar_one_or_none()
            if existing:
                return existing

        entry = CustomerLedger(
            customer_id=customer_id,
            type=LedgerTransactionType.PAYMENT,
            amount=amount,
            payment_method=payment_method,
            note=idempotency_key,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list_ledger_entries(
        self,
        customer_id: UUID,
        page: int = 1,
        page_size: int = 50,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[CustomerLedger], int]:
        """List ledger entries with filters."""
        query = (
            select(CustomerLedger)
            .where(CustomerLedger.customer_id == customer_id)
            .order_by(CustomerLedger.created_at.desc())
        )

        if start_date:
            query = query.where(cast(CustomerLedger.created_at, Date) >= start_date)
        if end_date:
            query = query.where(cast(CustomerLedger.created_at, Date) <= end_date)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        entries = result.scalars().all()

        return list(entries), total
