from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin
from app.models.product_details import ProductDetailsOut
from app.models.tags import TagOut
from app.models.menu_categories import MenuCategoryOut


class ProductBase(CoreModel):
    name: Annotated[
        str, Field(..., json_schema_extra={'example': 'Chicken Sandwich'})
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'Bread, cheese, lettuce, tomato, and chicken.'
        })
    ]
    image_url: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra={
            'example': 'https://domain.com/path/image.png'
        })
    ]
    price: Annotated[float, Field(..., json_schema_extra={'example': 4.29})]


class ProductCreate(ProductBase):
    has_details: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    is_public: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class ProductUpdate(ProductBase):
    pass


class ProductInDB(IDModelMixin, ProductBase):
    view_count: Annotated[int, Field(..., json_schema_extra={'example': 10})]
    has_details: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    is_public: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class ProductPublic(IDModelMixin, ProductBase):
    pass


class ProductOutDetailed(ProductBase):
    is_public: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
    details: ProductDetailsOut
    tags: list[TagOut]
    menu_categories: list[MenuCategoryOut]
