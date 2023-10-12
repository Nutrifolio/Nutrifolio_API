from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin


class ProductDetailsBase(CoreModel):
    calories: Annotated[
        Optional[int], 
        Field(default=None, json_schema_extra={'example': 450})
    ]
    protein: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 18.5})
    ]
    carbs: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 42.5})
    ]
    fiber: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 2.5})
    ]
    sugars: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 5.5})
    ]
    fat: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 10.5})
    ]
    saturated_fat: Annotated[
        Optional[float],
        Field(default=None, json_schema_extra={'example': 1.5})
    ]


class ProductDetailsCreate(ProductDetailsBase):
    product_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class ProductDetailsInDB(IDModelMixin, ProductDetailsBase):
    product_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class ProductDetailsOut(ProductDetailsBase):
    pass
