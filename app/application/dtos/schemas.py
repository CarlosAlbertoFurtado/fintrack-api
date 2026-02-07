from datetime import datetime

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
    avatar_url: str | None = None


class AuthResponseDTO(BaseModel):
    user: UserResponseDTO
    access_token: str
    refresh_token: str


# --- Transactions ---

class CreateTransactionDTO(BaseModel):
    description: str = Field(min_length=2, max_length=255)
    amount: float = Field(gt=0)
    type: str = Field(pattern="^(INCOME|EXPENSE)$")
    category_id: str | None = None
    date: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)
    is_recurring: bool = False
    recurring_day: int | None = Field(default=None, ge=1, le=31)


class UpdateTransactionDTO(BaseModel):
    description: str | None = Field(default=None, min_length=2, max_length=255)
    amount: float | None = Field(default=None, gt=0)
    type: str | None = Field(default=None, pattern="^(INCOME|EXPENSE)$")
    category_id: str | None = None
    notes: str | None = Field(default=None, max_length=500)


class TransactionResponseDTO(BaseModel):
    id: str
    description: str
    amount: float
    type: str
    category_id: str | None
    date: datetime
    notes: str | None
    is_recurring: bool
    created_at: datetime


# --- Categories ---

class CreateCategoryDTO(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    type: str = Field(pattern="^(INCOME|EXPENSE)$")
    icon: str | None = None
    color: str = Field(default="#6366F1", pattern="^#[0-9A-Fa-f]{6}$")


class CategoryResponseDTO(BaseModel):
    id: str
    name: str
    type: str
    icon: str | None
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
    icon: str | None
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
