"""Dependency injection wiring. Connects interfaces to implementations."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.cache.redis_cache import RedisCacheService
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.budget_repository import SQLAlchemyBudgetRepository
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.repositories.transaction_repository import SQLAlchemyTransactionRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.ai_categorizer import OpenAICategorizerService

_cache = RedisCacheService()
_ai = OpenAICategorizerService()


def get_cache_service() -> RedisCacheService:
    return _cache


def get_ai_service() -> OpenAICategorizerService:
    return _ai


def get_user_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_transaction_repository(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyTransactionRepository:
    return SQLAlchemyTransactionRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(db)


def get_budget_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyBudgetRepository:
    return SQLAlchemyBudgetRepository(db)
