import pytest

from app.domain.entities.transaction import Transaction, TransactionType


class TestTransaction:
    @pytest.fixture
    def props(self):
        return {
            "description": "Supermercado Extra",
            "amount": 150.50,
            "type": TransactionType.EXPENSE,
            "user_id": "user-123",
            "category_id": "cat-456",
        }

    def test_create_valid(self, props):
        tx = Transaction(**props)
        assert tx.description == "Supermercado Extra"
        assert tx.amount == 150.50
        assert tx.type == TransactionType.EXPENSE

    def test_short_description_raises(self, props):
        props["description"] = "A"
        with pytest.raises(ValueError, match="at least 2"):
            Transaction(**props)

    def test_zero_amount_raises(self, props):
        props["amount"] = 0
        with pytest.raises(ValueError, match="greater than zero"):
            Transaction(**props)

    def test_negative_amount_raises(self, props):
        props["amount"] = -100
        with pytest.raises(ValueError, match="greater than zero"):
            Transaction(**props)

    def test_missing_user_id_raises(self, props):
        props["user_id"] = ""
        with pytest.raises(ValueError, match="User ID"):
            Transaction(**props)

    def test_income_type(self, props):
        props["type"] = TransactionType.INCOME
        tx = Transaction(**props)
        assert tx.is_income()
        assert not tx.is_expense()

    def test_expense_type(self, props):
        tx = Transaction(**props)
        assert tx.is_expense()
        assert not tx.is_income()

    def test_signed_amount(self, props):
        expense = Transaction(**props)
        assert expense.get_signed_amount() == -150.50

        props["type"] = TransactionType.INCOME
        income = Transaction(**props)
        assert income.get_signed_amount() == 150.50

    def test_formatted_brl(self, props):
        tx = Transaction(**props)
        assert "R$" in tx.get_formatted_amount()

    def test_invalid_recurring_day(self, props):
        props["is_recurring"] = True
        props["recurring_day"] = 32
        with pytest.raises(ValueError, match="between 1 and 31"):
            Transaction(**props)
