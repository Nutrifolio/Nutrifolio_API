from typing import List
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.products import ProductCreate, ProductInDB
from app.api.enums.products import SortByOption, SortOrderOption


FILTER_PRODUCTS_FROM_NEARBY_STORES_QUERY = """
    SELECT
        p.id, p.name, p.description, p.image_url, p.price, p.view_count,
        p.has_details, p.is_public, p.store_id
    FROM products AS p
        INNER JOIN product_tags AS pt ON pt.product_id = p.id
        INNER JOIN product_menu_categories AS pmc ON pmc.product_id = p.id
    WHERE store_id = ANY (:store_ids)
        AND pt.tag_id = ANY (:tag_ids)
        AND pmc.menu_category_id = ANY (:menu_category_ids)
        AND p.price BETWEEN :min_price AND :max_price
        AND p.is_public = TRUE
    GROUP BY p.id
    HAVING COUNT(DISTINCT pt.tag_id) = :tag_count;
"""

GET_PRODUCT_BY_ID_QUERY = """
    SELECT
        id, name, description, image_url, price,
        view_count, has_details, is_public, store_id
    FROM products
    WHERE id = :id;
"""

GET_PRODUCT_BY_NAME_AND_STORE_ID_QUERY = """
    SELECT
        id, name, description, image_url, price,
        view_count, has_details, is_public, store_id
    FROM products
    WHERE name = :name AND store_id = :store_id;
"""

CREATE_PRODUCT_QUERY = """
    INSERT INTO products (
        name, description, image_url, price, has_details, is_public, store_id
    )
    VALUES (
        :name, :description, :image_url, :price, :has_details, :is_public, :store_id
    )
    RETURNING
        id, name, description, image_url, price,
        view_count, has_details, is_public, store_id;
"""

INCREMENT_PRODUCT_VIEW_COUNT_BY_ID_QUERY = """
    UPDATE products
    SET view_count = view_count + 1
    WHERE id = :id;
"""


class ProductsRepository(BaseRepository):
    """"
    All database actions associated with the Product resource
    """

    async def filter_products_from_nearby_stores(
        self,
        *,
        store_ids: list[int],
        tag_ids: list[int],
        menu_category_ids: list[int],
        min_price: float,
        max_price: float
    ) -> List[ProductInDB]:
        product_records = await self.db.fetch_all(
            query=FILTER_PRODUCTS_FROM_NEARBY_STORES_QUERY,
            values={
                "store_ids": store_ids,
                "tag_ids": tag_ids,
                "menu_category_ids": menu_category_ids,
                "min_price": min_price,
                "max_price": max_price,
                "tag_count": len(tag_ids)
            }
        )
        return [ProductInDB(**product) for product in product_records]


    async def get_product_by_id(self, *, id: int) -> ProductInDB:
        product_record = await self.db.fetch_one(
            query=GET_PRODUCT_BY_ID_QUERY, values={"id": id}
        )

        if not product_record:
            return None

        return ProductInDB(**product_record)


    async def get_product_by_name_and_store_id(
        self, *, name: str, store_id:int
    ) -> ProductInDB:
        product_record = await self.db.fetch_one(
            query=GET_PRODUCT_BY_NAME_AND_STORE_ID_QUERY, 
            values={"name": name, "store_id": store_id}
        )

        if not product_record:
            return None

        return ProductInDB(**product_record)


    async def create_product(self, *, new_product: ProductCreate) -> ProductInDB:
        product_record = await self.db.fetch_one(
            query=CREATE_PRODUCT_QUERY, values=new_product.model_dump()
        )

        return ProductInDB(**product_record)


    async def increment_product_view_count_by_id(self, *, id=id) -> ProductInDB:
        product_record = await self.db.fetch_one(
            query=INCREMENT_PRODUCT_VIEW_COUNT_BY_ID_QUERY,
            values={"id": id}
        )

        if not product_record:
            return None

        return ProductInDB(**product_record)
