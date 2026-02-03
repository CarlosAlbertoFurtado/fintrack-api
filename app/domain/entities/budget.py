from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Budget:
    user_id: str
    category_id: str
    amount: float
    month: int  # 1-12
    year: int
    id: str = field(default_factory=lambda: str(uuid4()))
    spent: float = 0.0
    alert_threshold: float = 0.8  # padrão 80%, configurável por orçamento
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.amount <= 0:
            raise ValueError("Budget amount must be greater than zero")
        if not 1 <= self.month <= 12:
            raise ValueError("Month must be between 1 and 12")
        if self.year < 2020:
            raise ValueError("Year must be 2020 or later")
        if not 0.0 <= self.alert_threshold <= 1.0:
            raise ValueError("Alert threshold must be between 0.0 and 1.0")

    @property
    def remaining(self) -> float:
        return max(0, self.amount - self.spent)

    @property
    def percentage_used(self) -> float:
        if self.amount == 0:
            return 0.0
        return min(100.0, (self.spent / self.amount) * 100)

    def is_over_budget(self) -> bool:
        return self.spent > self.amount

    def should_alert(self) -> bool:
        return self.percentage_used >= (self.alert_threshold * 100)

    def get_status(self) -> str:
        pct = self.percentage_used
        if pct >= 100:
            return "OVER_BUDGET"
        if pct >= self.alert_threshold * 100:
            return "WARNING"
        if pct >= 50:
            return "MODERATE"
        return "HEALTHY"
