from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.application.dtos.schemas import (
    CreateTransactionDTO, UpdateTransactionDTO,
    TransactionResponseDTO, PaginatedResponseDTO,
)
from app.application.use_cases.create_transaction import CreateTransactionUseCase
from app.domain.entities.transaction import TransactionType
from app.domain.interfaces.repositories import PaginationParams, TransactionFilters
from app.presentation.dependencies import (
    get_transaction_repository, get_category_repository,
    get_cache_service, get_ai_service,
)
from app.presentation.middlewares.auth import get_current_user
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.cache.redis_cache import RedisCacheService
from app.infrastructure.services.ai_categorizer import OpenAICategorizerService
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _serialize(t) -> dict:
    """Map a domain Transaction to a response dict."""
    return TransactionResponseDTO(
        id=t.id, description=t.description, amount=t.amount,
        type=t.type.value, category_id=t.category_id,
        date=t.date, notes=t.notes, is_recurring=t.is_recurring,
        created_at=t.created_at,
    ).model_dump()


@router.post("/", response_model=TransactionResponseDTO, status_code=201)
async def create(
    dto: CreateTransactionDTO,
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    cat_repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
    cache: RedisCacheService = Depends(get_cache_service),
    ai: OpenAICategorizerService = Depends(get_ai_service),
):
    uc = CreateTransactionUseCase(tx_repo, cat_repo, cache, ai)
    tx = await uc.execute(current_user["user_id"], dto)
    return _serialize(tx)


@router.get("/", response_model=PaginatedResponseDTO)
async def list_all(
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, pattern="^(INCOME|EXPENSE)$"),
    category_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
):
    filters = TransactionFilters(
        user_id=current_user["user_id"],
        type=TransactionType(type) if type else None,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )
    result = await tx_repo.find_all(PaginationParams(page=page, limit=limit), filters)
    return PaginatedResponseDTO(
        data=[_serialize(t) for t in result.data],
        total=result.total, page=result.page,
        limit=result.limit, total_pages=result.total_pages,
    )


@router.get("/{transaction_id}", response_model=TransactionResponseDTO)
async def get_by_id(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
):
    tx = await tx_repo.find_by_id(transaction_id)
    if not tx or tx.user_id != current_user["user_id"]:
        raise NotFoundError("Transaction")
    return _serialize(tx)


@router.put("/{transaction_id}", response_model=TransactionResponseDTO)
async def update(
    transaction_id: str,
    dto: UpdateTransactionDTO,
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    cache: RedisCacheService = Depends(get_cache_service),
):
    existing = await tx_repo.find_by_id(transaction_id)
    if not existing or existing.user_id != current_user["user_id"]:
        raise NotFoundError("Transaction")

    updated = await tx_repo.update(transaction_id, **dto.model_dump(exclude_unset=True))
    await cache.delete_pattern(f"summary:{current_user['user_id']}:*")
    return _serialize(updated)


@router.delete("/{transaction_id}", status_code=204)
async def delete(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    tx_repo: SQLAlchemyTransactionRepository = Depends(get_transaction_repository),
    cache: RedisCacheService = Depends(get_cache_service),
):
    existing = await tx_repo.find_by_id(transaction_id)
    if not existing or existing.user_id != current_user["user_id"]:
        raise NotFoundError("Transaction")
    await tx_repo.delete(transaction_id)
    await cache.delete_pattern(f"summary:{current_user['user_id']}:*")
