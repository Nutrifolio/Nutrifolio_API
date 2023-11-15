from typing import Annotated, Optional
from pydantic import Field
from app.models.core import CoreModel, IDModelMixin
from app.models.product_details import ProductDetailsOut
from app.models.tags import TagOut
from app.models.menu_categories import MenuCategoryOut
from app.models.store_profiles import StoreProfileOutProductDetailed, StoreProfileOutFilter
from app.api.enums.products import MaxDistanceOption, SortByOption


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


class ProductOutCreate(IDModelMixin, ProductBase):
    is_public: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]
    details: ProductDetailsOut
    tags: list[TagOut]
    menu_categories: list[MenuCategoryOut]


class ProductInDB(IDModelMixin, ProductBase):
    view_count: Annotated[int, Field(..., json_schema_extra={'example': 10})]
    has_details: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    is_public: Annotated[bool, Field(..., json_schema_extra={'example': True})]
    store_id: Annotated[int, Field(..., json_schema_extra={'example': 1})]


class ProductDetailed(IDModelMixin, ProductBase):
    store: StoreProfileOutProductDetailed
    details: ProductDetailsOut
    tags: list[TagOut]
    menu_categories: list[MenuCategoryOut]


class ProductDetailedOut(CoreModel):
    product: ProductDetailed


class Filters(CoreModel):
    lat: Annotated[float, Field(..., json_schema_extra={'example': 38.011726})]
    lng: Annotated[float, Field(..., json_schema_extra={'example': 23.822457})]
    tag_ids: Annotated[
        list[int],
        Field(..., json_schema_extra={'example': [1, 2, 4]})
    ]
    menu_category_ids: Annotated[
        list[int],
        Field(..., json_schema_extra={'example': [1, 2]})
    ]
    max_dist: Annotated[MaxDistanceOption, Field(..., json_schema_extra={
        'example': 3
    })]
    min_price: Annotated[float, Field(..., json_schema_extra={'example': 0.00})]
    max_price: Annotated[float, Field(..., json_schema_extra={'example': 10.00})]
    sort_by: Annotated[SortByOption, Field(..., json_schema_extra={
        'example': 'product_view_count'
    })]


class ProductOutFilter(IDModelMixin, ProductBase):
    store: StoreProfileOutFilter
    tags: list[TagOut]


class ProductsByMenuCategory(CoreModel):
    menu_category: MenuCategoryOut
    products: list[ProductOutFilter]


class FilterOut(CoreModel):
    products_by_menu_categories: list[ProductsByMenuCategory]


class ProductOutStore(IDModelMixin, ProductBase):
    tags: list[TagOut]


class ProductsByMenuCategoryStore(CoreModel):
    menu_category: MenuCategoryOut
    products: list[ProductOutStore]
