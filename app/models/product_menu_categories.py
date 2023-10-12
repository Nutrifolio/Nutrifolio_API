from typing import Annotated
from pydantic import Field
from app.models.core import CoreModel


class ProductMenuCategoryBase(CoreModel):
    product_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
    menu_category_id: Annotated[int, Field(..., json_schema_extra={'example': 2})]


class ProductMenuCategoryCreate(ProductMenuCategoryBase):
    pass


class ProductMenuCategoryInDB(ProductMenuCategoryBase):
    pass
