from fastapi import APIRouter
from app.core.logging import get_logger


router = APIRouter()

products_logger = get_logger(__name__)


import app.api.routes.products.create_product
import app.api.routes.products.get_product_by_id
import app.api.routes.products.delete_product_by_id
import app.api.routes.products.filter_products_from_nearby_stores
