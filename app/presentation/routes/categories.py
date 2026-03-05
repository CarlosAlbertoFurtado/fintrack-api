from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.application.dtos.schemas import CreateCategoryDTO, CategoryResponseDTO
from app.domain.entities.category import Category, CategoryType
from app.presentation.dependencies import get_category_repository
from app.presentation.middlewares.auth import get_current_user
from app.infrastructure.repositories.category_repository import SQLAlchemyCategoryRepository
from app.shared.errors import NotFoundError

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponseDTO, status_code=201)
async def create(
    dto: CreateCategoryDTO,
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
):
    category = Category(
        name=dto.name.strip(), type=CategoryType(dto.type),
        icon=dto.icon, color=dto.color, user_id=current_user["user_id"],
    )
    created = await repo.create(category)
    return CategoryResponseDTO(
        id=created.id, name=created.name, type=created.type.value,
        icon=created.icon, color=created.color, is_default=created.is_default,
    )


@router.get("/", response_model=list[CategoryResponseDTO])
async def list_all(
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
    type: Optional[str] = None,
):
    cat_type = CategoryType(type) if type else None
    categories = await repo.find_by_user(current_user["user_id"], cat_type)
    return [
        CategoryResponseDTO(
            id=c.id, name=c.name, type=c.type.value,
            icon=c.icon, color=c.color, is_default=c.is_default,
        )
        for c in categories
    ]


@router.delete("/{category_id}", status_code=204)
async def delete(
    category_id: str,
    current_user: dict = Depends(get_current_user),
    repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
):
    category = await repo.find_by_id(category_id)
    if not category or category.user_id != current_user["user_id"]:
        raise NotFoundError("Category")
    if category.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default categories")
    await repo.delete(category_id)
