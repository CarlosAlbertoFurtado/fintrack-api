from datetime import datetime

from app.application.dtos.schemas import BudgetResponseDTO, CreateBudgetDTO
from app.domain.entities.budget import Budget
from app.domain.interfaces.repositories import IBudgetRepository, ITransactionRepository
from app.shared.errors import ConflictError


class CreateBudgetUseCase:
    def __init__(self, budget_repo: IBudgetRepository, transaction_repo: ITransactionRepository):
        self.budget_repo = budget_repo
        self.transaction_repo = transaction_repo

    async def execute(self, user_id: str, dto: CreateBudgetDTO) -> BudgetResponseDTO:
        existing = await self.budget_repo.find_by_user_and_month(user_id, dto.month, dto.year)
        if any(b.category_id == dto.category_id for b in existing):
            raise ConflictError("Budget already exists for this category/month")

        # check how much was already spent this month
        start = datetime(dto.year, dto.month, 1)
        if dto.month == 12:
            end = datetime(dto.year + 1, 1, 1)
        else:
            end = datetime(dto.year, dto.month + 1, 1)

        summary = await self.transaction_repo.get_summary(user_id, start, end)
        spent = summary.get("total_expenses", 0.0)

        budget = Budget(
            user_id=user_id,
            category_id=dto.category_id,
            amount=dto.amount,
            spent=spent,
            month=dto.month,
            year=dto.year,
            alert_threshold=dto.alert_threshold,
        )

        created = await self.budget_repo.create(budget)

        return BudgetResponseDTO(
            id=created.id,
            category_id=created.category_id,
            amount=created.amount,
            spent=created.spent,
            remaining=created.remaining,
            percentage_used=created.percentage_used,
            status=created.get_status(),
            month=created.month,
            year=created.year,
        )
