from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.category import DEFAULT_CATEGORIES, Category, CategoryType
from app.domain.interfaces.repositories import ICategoryRepository
from app.infrastructure.database.models import CategoryModel


class SQLAlchemyCategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            type=CategoryType(model.type),
            icon=model.icon,
            color=model.color,
            is_default=model.is_default,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, category: Category) -> Category:
        model = CategoryModel(
            id=category.id,
            name=category.name,
            type=category.type.value,
            icon=category.icon,
            color=category.color,
            is_default=category.is_default,
            user_id=category.user_id,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, category_id: str) -> Category | None:
        result = await self.session.get(CategoryModel, category_id)
        return self._to_domain(result) if result else None

    async def find_by_user(
        self, user_id: str, type: CategoryType | None = None
    ) -> list[Category]:
        query = select(CategoryModel).where(CategoryModel.user_id == user_id)
        if type:
            query = query.where(CategoryModel.type == type.value)
        query = query.order_by(CategoryModel.name.asc())

        result = await self.session.execute(query)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def update(self, category_id: str, **kwargs: object) -> Category:
        model = await self.session.get(CategoryModel, category_id)
        if not model:
            raise ValueError(f"Category {category_id} not found")
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, category_id: str) -> None:
        model = await self.session.get(CategoryModel, category_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def create_defaults(self, user_id: str) -> list[Category]:
        """Seed the 12 default categories for a new user."""
        categories = []
        for cat in DEFAULT_CATEGORIES:
            icon = cat["icon"].value if hasattr(cat["icon"], "value") else cat["icon"]
            model = CategoryModel(
                id=str(uuid4()),
                name=cat["name"],
                type=cat["type"].value,
                icon=icon,
                color=cat["color"],
                is_default=True,
                user_id=user_id,
            )
            self.session.add(model)
            categories.append(self._to_domain(model))
        await self.session.flush()
        return categories
