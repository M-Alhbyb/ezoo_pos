from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.expenses.service import ExpenseService
from app.schemas.expense import ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/api/expenses", tags=["expenses"])


def get_expense_service(db: AsyncSession = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    data: ExpenseCreate,
    service: ExpenseService = Depends(get_expense_service),
):
    try:
        return await service.create_expense(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
