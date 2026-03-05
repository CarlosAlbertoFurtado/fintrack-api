from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Auth ---

class RegisterDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(min_length=2, max_length=100)


class LoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponseDTO(BaseModel):
    id: str
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None


class AuthResponseDTO(BaseModel):
    user: UserResponseDTO
    access_token: str
    refresh_token: str


# --- Transactions ---

class CreateTransactionDTO(BaseModel):
    description: str = Field(min_length=2, max_length=255)
    amount: float = Field(gt=0)
    type: str = Field(pattern="^(INCOME|EXPENSE)$")
    category_id: Optional[str] = None
    date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    is_recurring: bool = False
    recurring_day: Optional[int] = Field(default=None, ge=1, le=31)


class UpdateTransactionDTO(BaseModel):
    description: Optional[str] = Field(default=None, min_length=2, max_length=255)
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[str] = Field(default=None, pattern="^(INCOME|EXPENSE)$")
    category_id: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class TransactionResponseDTO(BaseModel):
    id: str
    description: str
    amount: float
    type: str
    category_id: Optional[str]
    date: datetime
    notes: Optional[str]
    is_recurring: bool
    created_at: datetime


# --- Categories ---

class CreateCategoryDTO(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: str = Field(pattern="^(INCOME|EXPENSE)$")
    icon: Optional[str] = None
    color: str = Field(default="#6366F1", pattern="^#[0-9A-Fa-f]{6}$")


class CategoryResponseDTO(BaseModel):
    id: str
    name: str
    type: str
    icon: Optional[str]
    color: str
    is_default: bool


# --- Budgets ---

class CreateBudgetDTO(BaseModel):
    category_id: str
    amount: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020)
    alert_threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class BudgetResponseDTO(BaseModel):
    id: str
    category_id: str
    amount: float
    spent: float
    remaining: float
    percentage_used: float
    status: str
    month: int
    year: int


# --- Reports ---

class SummaryResponseDTO(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
    transaction_count: int
    period_from: datetime
    period_to: datetime


class CategoryBreakdownDTO(BaseModel):
    category: str
    icon: Optional[str]
    color: str
    type: str
    total: float
    count: int
    percentage: float = 0.0


# --- Shared ---

class PaginatedResponseDTO(BaseModel):
    data: list
    total: int
    page: int
    limit: int
    total_pages: int
