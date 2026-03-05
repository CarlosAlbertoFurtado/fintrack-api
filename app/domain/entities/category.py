from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class CategoryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


# Emojis as icons — kept simple on purpose (no external icon lib needed)
CATEGORY_ICONS = {
    "salary": "💰",
    "food": "🍔",
    "transport": "🚗",
    "health": "🏥",
    "education": "📚",
    "entertainment": "🎮",
    "housing": "🏠",
    "shopping": "🛍️",
    "freelance": "💼",
    "investment": "📈",
    "bills": "📄",
    "other": "📦",
}

# Created automatically for every new user
DEFAULT_CATEGORIES = [
    {"name": "Salário", "type": CategoryType.INCOME, "icon": "💰", "color": "#22C55E"},
    {"name": "Freelance", "type": CategoryType.INCOME, "icon": "💼", "color": "#3B82F6"},
    {"name": "Investimentos", "type": CategoryType.INCOME, "icon": "📈", "color": "#8B5CF6"},
    {"name": "Alimentação", "type": CategoryType.EXPENSE, "icon": "🍔", "color": "#EF4444"},
    {"name": "Transporte", "type": CategoryType.EXPENSE, "icon": "🚗", "color": "#F59E0B"},
    {"name": "Saúde", "type": CategoryType.EXPENSE, "icon": "🏥", "color": "#EC4899"},
    {"name": "Educação", "type": CategoryType.EXPENSE, "icon": "📚", "color": "#6366F1"},
    {"name": "Lazer", "type": CategoryType.EXPENSE, "icon": "🎮", "color": "#14B8A6"},
    {"name": "Moradia", "type": CategoryType.EXPENSE, "icon": "🏠", "color": "#F97316"},
    {"name": "Compras", "type": CategoryType.EXPENSE, "icon": "🛍️", "color": "#E11D48"},
    {"name": "Contas", "type": CategoryType.EXPENSE, "icon": "📄", "color": "#64748B"},
    {"name": "Outros", "type": CategoryType.EXPENSE, "icon": "📦", "color": "#94A3B8"},
]


@dataclass
class Category:
    name: str
    type: CategoryType
    user_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    icon: Optional[str] = None
    color: str = "#6366F1"
    is_default: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Category name must be at least 2 characters")
        if not self.user_id:
            raise ValueError("User ID is required")
        if self.color and not self.color.startswith("#"):
            raise ValueError("Color must be a hex code starting with #")
