from fastapi import APIRouter
from app.api.routes.users import router as users_router
from app.api.routes.stores import router as stores_router
from app.api.routes.products import router as products_router
from app.api.routes.tags import router as tags_router
from app.api.routes.menu_categories import router as menu_categories_router


router = APIRouter()


router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(stores_router, prefix="/stores", tags=["Stores"])
router.include_router(products_router, prefix="/products", tags=["Products"])
router.include_router(tags_router, prefix="/tags", tags=["Tags"])
router.include_router(menu_categories_router, prefix="/menu_categories", tags=["Menu Categories"])
