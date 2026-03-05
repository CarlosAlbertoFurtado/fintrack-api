"""Unit tests for CreateTransactionUseCase with mocked dependencies."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.dtos.schemas import CreateTransactionDTO
from app.application.use_cases.create_transaction import CreateTransactionUseCase
from app.domain.entities.budget import Budget
from app.domain.entities.category import Category, CategoryType
from app.domain.entities.transaction import Transaction, TransactionType
from app.shared.errors import NotFoundError


@pytest.fixture
def mock_deps():
    """Create mocked repository dependencies."""
    return {
        "transaction_repo": AsyncMock(),
        "category_repo": AsyncMock(),
        "budget_repo": AsyncMock(),
        "cache": AsyncMock(),
        "ai_service": AsyncMock(),
    }


@pytest.fixture
def use_case(mock_deps):
    return CreateTransactionUseCase(**mock_deps)


class TestCreateTransaction:
    @pytest.mark.asyncio
    async def test_creates_income_transaction(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Salary", amount=5000, type="INCOME",
        )
        mock_deps["transaction_repo"].create.return_value = Transaction(
            description="Salary", amount=5000,
            type=TransactionType.INCOME, user_id="u1",
        )

        result = await use_case.execute("u1", dto)

        assert result.description == "Salary"
        assert result.amount == 5000
        assert result.type == TransactionType.INCOME
        mock_deps["transaction_repo"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_expense_with_category(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Groceries", amount=200, type="EXPENSE",
            category_id="cat-1",
        )
        mock_deps["category_repo"].find_by_id.return_value = Category(
            id="cat-1", name="Food", type=CategoryType.EXPENSE,
            user_id="u1",
        )
        created_tx = Transaction(
            description="Groceries", amount=200,
            type=TransactionType.EXPENSE, user_id="u1",
            category_id="cat-1",
        )
        mock_deps["transaction_repo"].create.return_value = created_tx
        mock_deps["budget_repo"].find_by_user_and_month.return_value = []

        result = await use_case.execute("u1", dto)

        assert result.category_id == "cat-1"
        mock_deps["category_repo"].find_by_id.assert_called_once_with("cat-1")

    @pytest.mark.asyncio
    async def test_raises_not_found_for_invalid_category(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Test", amount=100, type="EXPENSE",
            category_id="nonexistent",
        )
        mock_deps["category_repo"].find_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await use_case.execute("u1", dto)

    @pytest.mark.asyncio
    async def test_auto_categorizes_when_no_category(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Uber ride", amount=30, type="EXPENSE",
        )
        mock_deps["ai_service"].categorize.return_value = "cat-transport"
        mock_deps["category_repo"].find_by_id.return_value = Category(
            id="cat-transport", name="Transport", type=CategoryType.EXPENSE,
            user_id="u1",
        )
        mock_deps["category_repo"].find_by_user.return_value = [
            Category(id="cat-transport", name="Transport",
                     type=CategoryType.EXPENSE, user_id="u1"),
        ]
        created_tx = Transaction(
            description="Uber ride", amount=30,
            type=TransactionType.EXPENSE, user_id="u1",
            category_id="cat-transport",
        )
        mock_deps["transaction_repo"].create.return_value = created_tx
        mock_deps["budget_repo"].find_by_user_and_month.return_value = []

        result = await use_case.execute("u1", dto)

        mock_deps["ai_service"].categorize.assert_called_once()
        assert result.category_id == "cat-transport"

    @pytest.mark.asyncio
    async def test_updates_budget_spent_on_expense(self, use_case, mock_deps):
        now = datetime.utcnow()
        dto = CreateTransactionDTO(
            description="Groceries", amount=150, type="EXPENSE",
            category_id="cat-food",
        )
        mock_deps["category_repo"].find_by_id.return_value = Category(
            id="cat-food", name="Food", type=CategoryType.EXPENSE,
            user_id="u1",
        )
        created_tx = Transaction(
            description="Groceries", amount=150,
            type=TransactionType.EXPENSE, user_id="u1",
            category_id="cat-food", date=now,
        )
        mock_deps["transaction_repo"].create.return_value = created_tx

        existing_budget = Budget(
            id="b1", user_id="u1", category_id="cat-food",
            amount=500, spent=100, month=now.month, year=now.year,
        )
        mock_deps["budget_repo"].find_by_user_and_month.return_value = [existing_budget]

        await use_case.execute("u1", dto)

        # spent should be updated: 100 + 150 = 250
        mock_deps["budget_repo"].update.assert_called_once_with("b1", spent=250)

    @pytest.mark.asyncio
    async def test_does_not_update_budget_for_income(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Freelance", amount=3000, type="INCOME",
        )
        mock_deps["transaction_repo"].create.return_value = Transaction(
            description="Freelance", amount=3000,
            type=TransactionType.INCOME, user_id="u1",
        )

        await use_case.execute("u1", dto)

        mock_deps["budget_repo"].find_by_user_and_month.assert_not_called()

    @pytest.mark.asyncio
    async def test_clears_cache_after_creation(self, use_case, mock_deps):
        dto = CreateTransactionDTO(
            description="Test", amount=50, type="INCOME",
        )
        mock_deps["transaction_repo"].create.return_value = Transaction(
            description="Test", amount=50,
            type=TransactionType.INCOME, user_id="u1",
        )

        await use_case.execute("u1", dto)

        assert mock_deps["cache"].delete_pattern.call_count == 2
