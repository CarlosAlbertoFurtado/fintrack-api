import pytest

from app.domain.entities.budget import Budget


class TestBudget:
    @pytest.fixture
    def props(self):
        return {
            "user_id": "user-123",
            "category_id": "cat-456",
            "amount": 1000.0,
            "month": 3,
            "year": 2026,
        }

    def test_create_valid(self, props):
        b = Budget(**props)
        assert b.amount == 1000.0
        assert b.remaining == 1000.0
        assert b.percentage_used == 0.0

    def test_remaining_after_spending(self, props):
        props["spent"] = 400.0
        b = Budget(**props)
        assert b.remaining == 600.0
        assert b.percentage_used == 40.0

    def test_over_budget(self, props):
        props["spent"] = 1200.0
        b = Budget(**props)
        assert b.is_over_budget()
        assert b.get_status() == "OVER_BUDGET"

    def test_warning_status(self, props):
        props["spent"] = 850.0
        b = Budget(**props)
        assert b.should_alert()
        assert b.get_status() == "WARNING"

    def test_healthy_status(self, props):
        props["spent"] = 200.0
        b = Budget(**props)
        assert not b.should_alert()
        assert b.get_status() == "HEALTHY"

    def test_moderate_status(self, props):
        props["spent"] = 600.0
        assert Budget(**props).get_status() == "MODERATE"

    def test_invalid_month(self, props):
        props["month"] = 13
        with pytest.raises(ValueError, match="between 1 and 12"):
            Budget(**props)

    def test_zero_amount(self, props):
        props["amount"] = 0
        with pytest.raises(ValueError, match="greater than zero"):
            Budget(**props)
