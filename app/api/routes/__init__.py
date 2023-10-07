from fastapi import APIRouter
from app.api.routes.users import router as users_router
from app.api.routes.products import router as products_router


router = APIRouter()


router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(products_router, prefix="/products", tags=["Products"])
