from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class TransactionType(StrEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


@dataclass
class Transaction:
    description: str
    amount: float
    type: TransactionType
    user_id: str
    category_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    date: datetime = field(default_factory=datetime.utcnow)
    notes: str | None = None
    is_recurring: bool = False
    recurring_day: int | None = None  # 1-31
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
        raw = f"{self.amount:,.2f}"
        formatted = raw.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{prefix} R$ {formatted}"
