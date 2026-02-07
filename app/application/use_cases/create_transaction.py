from datetime import datetime

from app.application.dtos.schemas import CreateTransactionDTO
from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.interfaces.repositories import (
    IAICategorizerService,
    IBudgetRepository,
    ICacheService,
    ICategoryRepository,
    ITransactionRepository,
)
from app.shared.errors import NotFoundError
from app.shared.logger import logger


class CreateTransactionUseCase:
    def __init__(
        self,
        transaction_repo: ITransactionRepository,
        category_repo: ICategoryRepository,
        budget_repo: IBudgetRepository,
        cache: ICacheService,
        ai_service: IAICategorizerService,
    ):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.budget_repo = budget_repo
        self.cache = cache
        self.ai_service = ai_service

    async def execute(self, user_id: str, dto: CreateTransactionDTO) -> Transaction:
        category_id = dto.category_id

        if not category_id:
            category_id = await self._auto_categorize(user_id, dto.description, dto.type)

        if category_id:
            cat = await self.category_repo.find_by_id(category_id)
            if not cat or cat.user_id != user_id:
                raise NotFoundError("Category")

        transaction = Transaction(
            description=dto.description.strip(),
            amount=dto.amount,
            type=TransactionType(dto.type),
            user_id=user_id,
            category_id=category_id or None,
            date=dto.date or datetime.utcnow(),
            notes=dto.notes,
            is_recurring=dto.is_recurring,
            recurring_day=dto.recurring_day,
        )

        created = await self.transaction_repo.create(transaction)

        if created.type == TransactionType.EXPENSE and created.category_id:
            await self._update_budget_spent(user_id, created)

        await self.cache.delete_pattern(f"summary:{user_id}:*")
        await self.cache.delete_pattern(f"transactions:{user_id}:*")

        return created

    async def _update_budget_spent(self, user_id: str, transaction: Transaction) -> None:
        tx_date = transaction.date
        budgets = await self.budget_repo.find_by_user_and_month(
            user_id, tx_date.month, tx_date.year,
        )
        for budget in budgets:
            if budget.category_id == transaction.category_id:
                new_spent = budget.spent + transaction.amount
                await self.budget_repo.update(budget.id, spent=new_spent)
                if budget.should_alert():
                    logger.info(
                        "budget_alert",
                        budget_id=budget.id,
                        percentage=budget.percentage_used,
                    )
                break

    async def _auto_categorize(self, user_id: str, description: str, tx_type: str) -> str | None:
        categories = await self.category_repo.find_by_user(user_id)
        matching = [
            {"id": c.id, "name": c.name, "type": c.type.value}
            for c in categories if c.type.value == tx_type
        ]
        if not matching:
            return None
        return await self.ai_service.categorize(description, matching)
