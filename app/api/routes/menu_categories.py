from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.logging import get_logger
from app.models.menu_categories import MenuCategoryOut, MenuCategoriesOut
from app.db.repositories.menu_categories import MenuCategoriesRepository
from app.api.dependencies.database import get_repository


router = APIRouter()

menu_categories_logger = get_logger(__name__)


@router.get(
    "/",
    response_model=MenuCategoriesOut,
    name="get-all-menu-categories"
)
async def get_all_menu_categories(
    menu_category_repo: Annotated[
        MenuCategoriesRepository,
        Depends(get_repository(MenuCategoriesRepository))
    ]
) -> MenuCategoriesOut:
    try:
        db_menu_categories = await menu_category_repo.get_all_menu_categories()
        return MenuCategoriesOut(
            menu_categories=[
                MenuCategoryOut(**menu_category.model_dump())
                for menu_category in db_menu_categories
            ]
        )
    except Exception as exc:
        menu_categories_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to fetch menu categories."
        )
