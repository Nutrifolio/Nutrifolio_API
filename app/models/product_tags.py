from typing import Annotated
from pydantic import Field
from app.models.core import CoreModel


class ProductTagBase(CoreModel):
    product_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
    tag_id: Annotated[int, Field(..., json_schema_extra={'example': 2})]


class ProductTagCreate(ProductTagBase):
    pass


class ProductTagInDB(ProductTagBase):
    pass
