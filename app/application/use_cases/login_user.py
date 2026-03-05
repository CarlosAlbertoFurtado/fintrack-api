from app.domain.interfaces.repositories import IUserRepository
from app.application.dtos.schemas import LoginDTO, AuthResponseDTO, UserResponseDTO
from app.shared.errors import UnauthorizedError
from app.shared.security import verify_password, generate_tokens


class LoginUserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, dto: LoginDTO) -> AuthResponseDTO:
        user = await self.user_repo.find_by_email(dto.email.lower().strip())
        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        if not user.password_hash:
            raise UnauthorizedError("This account uses social login")

        if not verify_password(dto.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        tokens = generate_tokens(user.id, user.role.value)
        await self.user_repo.update_refresh_token(user.id, tokens["refresh_token"])

        return AuthResponseDTO(
            user=UserResponseDTO(
                id=user.id, email=user.email,
                name=user.name, role=user.role.value,
                avatar_url=user.avatar_url,
            ),
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
