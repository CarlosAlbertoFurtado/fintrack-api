from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.budget import Budget
from app.domain.interfaces.repositories import IBudgetRepository
from app.infrastructure.database.models import BudgetModel


class SQLAlchemyBudgetRepository(IBudgetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: BudgetModel) -> Budget:
        return Budget(
            id=model.id,
            user_id=model.user_id,
            category_id=model.category_id,
            amount=model.amount,
            spent=model.spent,
            month=model.month,
            year=model.year,
            alert_threshold=model.alert_threshold,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, budget: Budget) -> Budget:
        model = BudgetModel(
            id=budget.id or str(uuid4()),
            user_id=budget.user_id,
            category_id=budget.category_id,
            amount=budget.amount,
            spent=budget.spent,
            month=budget.month,
            year=budget.year,
            alert_threshold=budget.alert_threshold,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, budget_id: str) -> Budget | None:
        result = await self.session.get(BudgetModel, budget_id)
        return self._to_domain(result) if result else None

    async def find_by_user_and_month(
        self, user_id: str, month: int, year: int,
    ) -> list[Budget]:
        query = (
            select(BudgetModel)
            .where(BudgetModel.user_id == user_id)
            .where(BudgetModel.month == month)
            .where(BudgetModel.year == year)
        )
        result = await self.session.execute(query)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def update(self, budget_id: str, **kwargs: object) -> Budget:
        model = await self.session.get(BudgetModel, budget_id)
        if not model:
            raise ValueError(f"Budget {budget_id} not found")
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, budget_id: str) -> None:
        model = await self.session.get(BudgetModel, budget_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()
