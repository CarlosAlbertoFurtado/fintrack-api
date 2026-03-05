from datetime import datetime

from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.interfaces.repositories import (
    ITransactionRepository, ICategoryRepository, ICacheService, IAICategorizerService,
)
from app.application.dtos.schemas import CreateTransactionDTO
from app.shared.errors import NotFoundError


class CreateTransactionUseCase:
    def __init__(
        self,
        transaction_repo: ITransactionRepository,
        category_repo: ICategoryRepository,
        cache: ICacheService,
        ai_service: IAICategorizerService,
    ):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.cache = cache
        self.ai_service = ai_service

    async def execute(self, user_id: str, dto: CreateTransactionDTO) -> Transaction:
        category_id = dto.category_id

        # if user didn't pick a category, try AI auto-categorization
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
            category_id=category_id or "",
            date=dto.date or datetime.utcnow(),
            notes=dto.notes,
            is_recurring=dto.is_recurring,
            recurring_day=dto.recurring_day,
        )

        created = await self.transaction_repo.create(transaction)

        # bust cached summaries so next request reflects the new transaction
        await self.cache.delete_pattern(f"summary:{user_id}:*")
        await self.cache.delete_pattern(f"transactions:{user_id}:*")

        return created

    async def _auto_categorize(self, user_id: str, description: str, tx_type: str) -> str | None:
        categories = await self.category_repo.find_by_user(user_id)
        matching = [
            {"id": c.id, "name": c.name, "type": c.type.value}
            for c in categories if c.type.value == tx_type
        ]
        if not matching:
            return None
        return await self.ai_service.categorize(description, matching)
