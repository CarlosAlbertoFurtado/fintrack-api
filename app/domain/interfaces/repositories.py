"""
Repository interfaces (ports).

Infrastructure layer provides concrete implementations.
Swapping database/ORM only requires changing the implementations,
not the use cases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Optional, TypeVar

from app.domain.entities.user import User, UserRole
from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.entities.category import Category, CategoryType
from app.domain.entities.budget import Budget

T = TypeVar("T")


@dataclass
class PaginationParams:
    page: int = 1
    limit: int = 20


@dataclass
class PaginatedResult(Generic[T]):
    data: list[T]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        return max(1, -(-self.total // self.limit))


class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def find_all(
        self, params: PaginationParams, role: Optional[UserRole] = None
    ) -> PaginatedResult[User]: ...

    @abstractmethod
    async def update(self, user_id: str, **kwargs: object) -> User: ...

    @abstractmethod
    async def delete(self, user_id: str) -> None: ...

    @abstractmethod
    async def update_refresh_token(self, user_id: str, token: Optional[str]) -> None: ...


@dataclass
class TransactionFilters:
    user_id: str
    type: Optional[TransactionType] = None
    category_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None


class ITransactionRepository(ABC):
    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction: ...

    @abstractmethod
    async def find_by_id(self, transaction_id: str) -> Optional[Transaction]: ...

    @abstractmethod
    async def find_all(
        self, params: PaginationParams, filters: TransactionFilters
    ) -> PaginatedResult[Transaction]: ...

    @abstractmethod
    async def update(self, transaction_id: str, **kwargs: object) -> Transaction: ...

    @abstractmethod
    async def delete(self, transaction_id: str) -> None: ...

    @abstractmethod
    async def get_summary(
        self, user_id: str, date_from: datetime, date_to: datetime
    ) -> dict[str, float]: ...

    @abstractmethod
    async def get_by_category(
        self, user_id: str, date_from: datetime, date_to: datetime
    ) -> list[dict[str, object]]: ...

    @abstractmethod
    async def get_monthly_trend(
        self, user_id: str, months: int = 6
    ) -> list[dict[str, object]]: ...


class ICategoryRepository(ABC):
    @abstractmethod
    async def create(self, category: Category) -> Category: ...

    @abstractmethod
    async def find_by_id(self, category_id: str) -> Optional[Category]: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: str, type: Optional[CategoryType] = None
    ) -> list[Category]: ...

    @abstractmethod
    async def update(self, category_id: str, **kwargs: object) -> Category: ...

    @abstractmethod
    async def delete(self, category_id: str) -> None: ...

    @abstractmethod
    async def create_defaults(self, user_id: str) -> list[Category]: ...


class IBudgetRepository(ABC):
    @abstractmethod
    async def create(self, budget: Budget) -> Budget: ...

    @abstractmethod
    async def find_by_id(self, budget_id: str) -> Optional[Budget]: ...

    @abstractmethod
    async def find_by_user_and_month(
        self, user_id: str, month: int, year: int
    ) -> list[Budget]: ...

    @abstractmethod
    async def update(self, budget_id: str, **kwargs: object) -> Budget: ...

    @abstractmethod
    async def delete(self, budget_id: str) -> None: ...


class ICacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]: ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> None: ...


class IAICategorizerService(ABC):
    @abstractmethod
    async def categorize(
        self, description: str, available_categories: list[dict[str, str]]
    ) -> Optional[str]: ...

    @abstractmethod
    async def generate_insights(
        self, transactions: list[dict[str, object]]
    ) -> str: ...
