from uuid import UUID
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerResponse,
    CustomerListResponse,
    LedgerListResponse,
    CustomerPaymentCreate,
    LedgerEntryResponse,
)
from app.modules.customers.service import CustomerService
from app.core.constants import LedgerTransactionType

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer."""
    service = CustomerService(db)
    return await service.create_customer(data)


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all customers with balances."""
    service = CustomerService(db)
    customers, total = await service.list_customers(page, page_size)
    return {"customers": customers, "total": total}


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get customer details with summary."""
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    summary = await service.get_customer_summary(customer_id)
    
    # Map to response and include summary
    response = CustomerResponse.model_validate(customer)
    response.summary = summary
    return response


@router.get("/{customer_id}/ledger", response_model=LedgerListResponse)
async def list_ledger(
    customer_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """List customer ledger entries."""
    service = CustomerService(db)
    entries, total = await service.list_ledger_entries(
        customer_id, page, page_size, start_date, end_date
    )
    return {"entries": entries, "total": total}


@router.post("/{customer_id}/payments", response_model=LedgerEntryResponse)
async def record_payment(
    customer_id: UUID,
    data: CustomerPaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Record a customer payment."""
    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    entry = await service.record_payment(
        customer_id=customer_id,
        amount=data.amount,
        payment_method=data.payment_method,
        note=data.note,
        idempotency_key=data.idempotency_key
    )
    
    return entry


@router.get("/report/summary", response_model=dict)
async def global_customer_report(
    db: AsyncSession = Depends(get_db)
):
    """T026: Global customer debt report."""
    from app.schemas.customer import CustomerListItem
    service = CustomerService(db)
    customers, total = await service.list_customers(page_size=1000)

    report = {
        "total_customers": total,
        "total_debt": sum(c.balance for c in customers),
        "customers": [
            {
                "id": str(c.id),
                "name": c.name,
                "phone": c.phone,
                "balance": float(c.balance),
                "credit_limit": float(c.credit_limit),
            }
            for c in customers
        ],
    }
    return report


@router.get("/{customer_id}/statement/pdf")
async def download_customer_statement_pdf(
    customer_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db)
):
    """T029: Generate and download PDF statement for a customer."""
    from fastapi.responses import Response
    from app.modules.reports.export_service import ExportService
    from app.schemas.customer import CustomerResponse

    service = CustomerService(db)
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    summary = await service.get_customer_summary(customer_id)
    entries, _ = await service.list_ledger_entries(customer_id, page_size=1000, start_date=start_date, end_date=end_date)

    customer_data = {
        "name": customer.name,
        "phone": customer.phone,
        "summary": {
            "total_sales": float(summary.total_sales),
            "total_payments": float(summary.total_payments),
            "total_returns": float(summary.total_returns),
            "balance": float(summary.balance),
        }
    }

    ledger_entries = [
        {
            "type": entry.type,
            "amount": float(entry.amount),
            "created_at": entry.created_at.isoformat() if entry.created_at else "",
            "note": entry.note,
        }
        for entry in entries
    ]

    export_service = ExportService()
    pdf_bytes = await export_service.generate_customer_statement_pdf(
        customer_data=customer_data,
        ledger_entries=ledger_entries,
        start_date=start_date,
        end_date=end_date,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="statement_{customer.name}_{customer_id}.pdf"'}
    )
