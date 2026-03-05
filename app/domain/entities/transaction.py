from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


@dataclass
class Transaction:
    description: str
    amount: float
    type: TransactionType
    user_id: str
    category_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    date: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    is_recurring: bool = False
    recurring_day: Optional[int] = None  # 1-31
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.description or len(self.description.strip()) < 2:
            raise ValueError("Description must be at least 2 characters")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if not self.user_id:
            raise ValueError("User ID is required")
        if not self.category_id:
            raise ValueError("Category ID is required")
        if self.is_recurring and self.recurring_day is not None:
            if not 1 <= self.recurring_day <= 31:
                raise ValueError("Recurring day must be between 1 and 31")

    def is_income(self) -> bool:
        return self.type == TransactionType.INCOME

    def is_expense(self) -> bool:
        return self.type == TransactionType.EXPENSE

    def get_signed_amount(self) -> float:
        """Negative for expenses, positive for income."""
        return self.amount if self.is_income() else -self.amount

    def get_formatted_amount(self) -> str:
        prefix = "+" if self.is_income() else "-"
        # TODO: use locale for proper BRL formatting
        return f"{prefix} R$ {self.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
