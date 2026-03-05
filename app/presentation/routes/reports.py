from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.application.dtos.schemas import SummaryResponseDTO, CategoryBreakdownDTO
from app.application.use_cases.get_financial_summary import GetFinancialSummaryUseCase
from app.domain.interfaces.repositories import PaginationParams, TransactionFilters
from app.presentation.dependencies import (
    get_transaction_repository, get_cache_service, get_ai_service,
)
from app.presentation.middlewares.auth import get_current_user
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.cache.redis_cache import RedisCacheService
from app.infrastructure.services.ai_categorizer import OpenAICategorizerService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/summary", response_model=SummaryResponseDTO)
async def summary(
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    cache: RedisCacheService = Depends(get_cache_service),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    uc = GetFinancialSummaryUseCase(tx_repo, cache)
    return await uc.execute(current_user["user_id"], date_from, date_to)


@router.get("/by-category", response_model=list[CategoryBreakdownDTO])
async def by_category(
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    now = datetime.utcnow()
    start = date_from or now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = date_to or now

    data = await tx_repo.get_by_category(current_user["user_id"], start, end)

    total_expense = sum(d["total"] for d in data if d["type"] == "EXPENSE")
    total_income = sum(d["total"] for d in data if d["type"] == "INCOME")

    result = []
    for d in data:
        base = total_expense if d["type"] == "EXPENSE" else total_income
        pct = (d["total"] / base * 100) if base > 0 else 0
        result.append(CategoryBreakdownDTO(
            category=d["category"], icon=d.get("icon"), color=d["color"],
            type=d["type"], total=d["total"], count=d["count"],
            percentage=round(pct, 1),
        ))
    return result


@router.get("/monthly-trend")
async def monthly_trend(
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    months: int = Query(6, ge=1, le=24),
):
    data = await tx_repo.get_monthly_trend(current_user["user_id"], months)
    return {"data": data}


@router.get("/insights")
async def ai_insights(
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    ai: OpenAICategorizerService = Depends(get_ai_service),
):
    """Generate AI-powered spending insights for the current month."""
    now = datetime.utcnow()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    result = await tx_repo.find_all(
        PaginationParams(page=1, limit=50),
        TransactionFilters(user_id=current_user["user_id"], date_from=start, date_to=now),
    )

    tx_data = [
        {"description": t.description, "amount": t.amount, "type": t.type.value,
         "category": t.category_id, "date": t.date.isoformat()}
        for t in result.data
    ]

    insights = await ai.generate_insights(tx_data)
    return {"insights": insights}
