from app.domain.entities.user import User, UserRole
from app.domain.interfaces.repositories import IUserRepository, ICategoryRepository
from app.application.dtos.schemas import RegisterDTO, AuthResponseDTO, UserResponseDTO
from app.shared.errors import ConflictError
from app.shared.security import hash_password, generate_tokens


class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, category_repo: ICategoryRepository):
        self.user_repo = user_repo
        self.category_repo = category_repo

    async def execute(self, dto: RegisterDTO) -> AuthResponseDTO:
        existing = await self.user_repo.find_by_email(dto.email)
        if existing:
            raise ConflictError("Email is already registered")

        user = User(
            email=dto.email.lower().strip(),
            name=dto.name.strip(),
            password_hash=hash_password(dto.password),
            role=UserRole.USER,
            is_active=True,
        )
        created = await self.user_repo.create(user)

        # every new user gets the default expense/income categories
        await self.category_repo.create_defaults(created.id)

        tokens = generate_tokens(created.id, created.role.value)
        await self.user_repo.update_refresh_token(created.id, tokens["refresh_token"])

        return AuthResponseDTO(
            user=UserResponseDTO(
                id=created.id, email=created.email,
                name=created.name, role=created.role.value,
                avatar_url=created.avatar_url,
            ),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
