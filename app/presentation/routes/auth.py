from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.application.dtos.schemas import AuthResponseDTO, LoginDTO, RegisterDTO, UserResponseDTO
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.presentation.dependencies import get_category_repository, get_user_repository
from app.presentation.middlewares.auth import get_current_user
from app.shared.security import decode_token, generate_tokens

router = APIRouter(prefix="/auth", tags=["Auth"])


class RefreshTokenDTO(BaseModel):
    refresh_token: str


@router.post("/register", response_model=AuthResponseDTO, status_code=201)
async def register(
    dto: RegisterDTO,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    category_repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
):
    use_case = RegisterUserUseCase(user_repo, category_repo)
    return await use_case.execute(dto)


@router.post("/login", response_model=AuthResponseDTO)
async def login(
    dto: LoginDTO,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = LoginUserUseCase(user_repo)
    return await use_case.execute(dto)


@router.get("/me", response_model=UserResponseDTO)
async def me(
    current_user: dict = Depends(get_current_user),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    user = await user_repo.find_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponseDTO(
        id=user.id, email=user.email, name=user.name,
        role=user.role.value, avatar_url=user.avatar_url,
    )


@router.post("/refresh", response_model=AuthResponseDTO)
async def refresh(
    dto: RefreshTokenDTO,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    """Rotate refresh token: validate old one, return new access + refresh pair."""
    try:
        payload = decode_token(dto.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from None

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user = await user_repo.find_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    tokens = generate_tokens(user.id, user.role.value)
    await user_repo.update_refresh_token(user.id, tokens["refresh_token"])

    return AuthResponseDTO(
        user=UserResponseDTO(
            id=user.id, email=user.email, name=user.name,
            role=user.role.value, avatar_url=user.avatar_url,
        ),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
    )
