from datetime import datetime

from fastapi import APIRouter, Depends

from app.application.dtos.schemas import CreateBudgetDTO, BudgetResponseDTO
from app.application.use_cases.create_budget import CreateBudgetUseCase
from app.presentation.dependencies import (
    get_transaction_repository, get_budget_repository,
)
from app.presentation.middlewares.auth import get_current_user
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponseDTO, status_code=201)
async def create(
    dto: CreateBudgetDTO,
    current_user: dict = Depends(get_current_user),
    budget_repo: SQLAlchemyBudgetRepository = Depends(get_budget_repository),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
):
    uc = CreateBudgetUseCase(budget_repo, tx_repo)
    return await uc.execute(current_user["user_id"], dto)


@router.get("/", response_model=list[BudgetResponseDTO])
async def list_by_month(
    current_user: dict = Depends(get_current_user),
    budget_repo: SQLAlchemyBudgetRepository = Depends(get_budget_repository),
    month: int = datetime.utcnow().month,
    year: int = datetime.utcnow().year,
):
    budgets = await budget_repo.find_by_user_and_month(
        current_user["user_id"], month, year,
    )
    return [
        BudgetResponseDTO(
            id=b.id, category_id=b.category_id, amount=b.amount,
            spent=b.spent, remaining=b.remaining,
            percentage_used=b.percentage_used,
            status=b.get_status(), month=b.month, year=b.year,
        )
        for b in budgets
    ]


@router.delete("/{budget_id}", status_code=204)
async def delete(
    budget_id: str,
    current_user: dict = Depends(get_current_user),
    budget_repo: SQLAlchemyBudgetRepository = Depends(get_budget_repository),
):
    budget = await budget_repo.find_by_id(budget_id)
    if not budget or budget.user_id != current_user["user_id"]:
        raise NotFoundError("Budget")
    await budget_repo.delete(budget_id)
