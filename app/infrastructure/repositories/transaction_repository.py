from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, extract, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.transaction import Transaction, TransactionType
from app.domain.interfaces.repositories import (
    ITransactionRepository, PaginationParams, PaginatedResult, TransactionFilters,
)
from app.infrastructure.database.models import TransactionModel, CategoryModel


class SQLAlchemyTransactionRepository(ITransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            description=model.description,
            amount=model.amount,
            type=TransactionType(model.type),
            date=model.date,
            notes=model.notes,
            is_recurring=model.is_recurring,
            recurring_day=model.recurring_day,
            user_id=model.user_id,
            category_id=model.category_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            id=transaction.id,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type.value,
            date=transaction.date,
            notes=transaction.notes,
            is_recurring=transaction.is_recurring,
            recurring_day=transaction.recurring_day,
            user_id=transaction.user_id,
            category_id=transaction.category_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        result = await self.session.get(TransactionModel, transaction_id)
        return self._to_domain(result) if result else None

    async def find_all(
        self, params: PaginationParams, filters: TransactionFilters
    ) -> PaginatedResult[Transaction]:
        query = select(TransactionModel).where(TransactionModel.user_id == filters.user_id)
        count_query = select(func.count()).select_from(TransactionModel).where(
            TransactionModel.user_id == filters.user_id
        )

        if filters.type:
            query = query.where(TransactionModel.type == filters.type.value)
            count_query = count_query.where(TransactionModel.type == filters.type.value)
        if filters.category_id:
            query = query.where(TransactionModel.category_id == filters.category_id)
            count_query = count_query.where(TransactionModel.category_id == filters.category_id)
        if filters.date_from:
            query = query.where(TransactionModel.date >= filters.date_from)
            count_query = count_query.where(TransactionModel.date >= filters.date_from)
        if filters.date_to:
            query = query.where(TransactionModel.date <= filters.date_to)
            count_query = count_query.where(TransactionModel.date <= filters.date_to)
        if filters.min_amount:
            query = query.where(TransactionModel.amount >= filters.min_amount)
            count_query = count_query.where(TransactionModel.amount >= filters.min_amount)
        if filters.max_amount:
            query = query.where(TransactionModel.amount <= filters.max_amount)
            count_query = count_query.where(TransactionModel.amount <= filters.max_amount)
        if filters.search:
            like = f"%{filters.search}%"
            query = query.where(TransactionModel.description.ilike(like))
            count_query = count_query.where(TransactionModel.description.ilike(like))

        query = query.order_by(TransactionModel.date.desc(), TransactionModel.created_at.desc())
        query = query.offset((params.page - 1) * params.limit).limit(params.limit)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)

        return PaginatedResult(
            data=[self._to_domain(row) for row in result.scalars().all()],
            total=total_result.scalar_one(),
            page=params.page,
            limit=params.limit,
        )

    async def update(self, transaction_id: str, **kwargs: object) -> Transaction:
        model = await self.session.get(TransactionModel, transaction_id)
        if not model:
            raise ValueError(f"Transaction {transaction_id} not found")
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, transaction_id: str) -> None:
        model = await self.session.get(TransactionModel, transaction_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def get_summary(
        self, user_id: str, date_from: datetime, date_to: datetime
    ) -> dict[str, float]:
        query = select(
            TransactionModel.type,
            func.sum(TransactionModel.amount).label("total"),
            func.count(TransactionModel.id).label("count"),
        ).where(
            and_(
                TransactionModel.user_id == user_id,
                TransactionModel.date >= date_from,
                TransactionModel.date <= date_to,
            )
        ).group_by(TransactionModel.type)

        result = await self.session.execute(query)

        summary: dict[str, float] = {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "balance": 0.0,
            "transaction_count": 0,
        }
        for row in result.all():
            if row.type == "INCOME":
                summary["total_income"] = float(row.total or 0)
            else:
                summary["total_expenses"] = float(row.total or 0)
            summary["transaction_count"] += int(row.count or 0)

        summary["balance"] = summary["total_income"] - summary["total_expenses"]
        return summary

    async def get_by_category(
        self, user_id: str, date_from: datetime, date_to: datetime
    ) -> list[dict[str, object]]:
        query = (
            select(
                CategoryModel.name.label("category_name"),
                CategoryModel.icon.label("category_icon"),
                CategoryModel.color.label("category_color"),
                TransactionModel.type,
                func.sum(TransactionModel.amount).label("total"),
                func.count(TransactionModel.id).label("count"),
            )
            .join(CategoryModel, TransactionModel.category_id == CategoryModel.id)
            .where(and_(
                TransactionModel.user_id == user_id,
                TransactionModel.date >= date_from,
                TransactionModel.date <= date_to,
            ))
            .group_by(
                CategoryModel.name, CategoryModel.icon,
                CategoryModel.color, TransactionModel.type,
            )
            .order_by(func.sum(TransactionModel.amount).desc())
        )

        result = await self.session.execute(query)
        return [
            {
                "category": row.category_name,
                "icon": row.category_icon,
                "color": row.category_color,
                "type": row.type,
                "total": float(row.total),
                "count": int(row.count),
            }
            for row in result.all()
        ]

    async def get_monthly_trend(self, user_id: str, months: int = 6) -> list[dict[str, object]]:
        query = (
            select(
                extract("year", TransactionModel.date).label("year"),
                extract("month", TransactionModel.date).label("month"),
                TransactionModel.type,
                func.sum(TransactionModel.amount).label("total"),
            )
            .where(TransactionModel.user_id == user_id)
            .group_by(
                extract("year", TransactionModel.date),
                extract("month", TransactionModel.date),
                TransactionModel.type,
            )
            .order_by(
                extract("year", TransactionModel.date).desc(),
                extract("month", TransactionModel.date).desc(),
            )
            .limit(months * 2)  # income + expense per month
        )

        result = await self.session.execute(query)
        return [
            {"year": int(row.year), "month": int(row.month), "type": row.type, "total": float(row.total)}
            for row in result.all()
        ]
