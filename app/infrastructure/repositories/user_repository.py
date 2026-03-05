
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User, UserRole
from app.domain.interfaces.repositories import IUserRepository, PaginatedResult, PaginationParams
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            password_hash=model.password_hash,
            avatar_url=model.avatar_url,
            role=UserRole(model.role),
            google_id=model.google_id,
            is_active=model.is_active,
            refresh_token=model.refresh_token,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            password_hash=entity.password_hash,
            avatar_url=entity.avatar_url,
            role=entity.role.value,
            google_id=entity.google_id,
            is_active=entity.is_active,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def find_by_id(self, user_id: str) -> User | None:
        result = await self.session.get(UserModel, user_id)
        return self._to_domain(result) if result else None

    async def find_by_email(self, email: str) -> User | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_all(
        self, params: PaginationParams, role: UserRole | None = None
    ) -> PaginatedResult[User]:
        query = select(UserModel)
        count_query = select(func.count()).select_from(UserModel)

        if role:
            query = query.where(UserModel.role == role.value)
            count_query = count_query.where(UserModel.role == role.value)

        query = query.order_by(UserModel.created_at.desc())
        query = query.offset((params.page - 1) * params.limit).limit(params.limit)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)

        return PaginatedResult(
            data=[self._to_domain(row) for row in result.scalars().all()],
            total=total_result.scalar_one(),
            page=params.page,
            limit=params.limit,
        )

    async def update(self, user_id: str, **kwargs: object) -> User:
        model = await self.session.get(UserModel, user_id)
        if not model:
            raise ValueError(f"User {user_id} not found")
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, user_id: str) -> None:
        model = await self.session.get(UserModel, user_id)
        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def update_refresh_token(self, user_id: str, token: str | None) -> None:
        model = await self.session.get(UserModel, user_id)
        if model:
            model.refresh_token = token
            await self.session.flush()
