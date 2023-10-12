from typing import List
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.products import ProductCreate, ProductUpdate, ProductInDB


GET_ALL_PRODUCTS_QUERY = "SELECT * FROM products;"

GET_PRODUCT_BY_ID_QUERY = "SELECT * FROM products WHERE id = :id;"

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

UPDATE_PRODUCT_BY_ID_QUERY = """
    UPDATE products
    SET name         = :name,
        description  = :description,
        price        = :price
    WHERE id = :id
    RETURNING id, name, description, price;
"""

DELETE_PRODUCT_BY_ID_QUERY = """
    DELETE FROM products 
    WHERE id = :id 
    RETURNING id;
"""


class ProductsRepository(BaseRepository):
    """"
    All database actions associated with the Product resource
    """

    async def get_all_products(self) -> List[ProductInDB]:
        product_records = await self.db.fetch_all(query=GET_ALL_PRODUCTS_QUERY)
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


    async def update_product_by_id(
        self, *, id: int, product_update: ProductUpdate
    ) -> ProductInDB:
        product = await self.get_product_by_id(id=id)

        if not product:
            return None

        product_update_params = product.model_copy(
            update=product_update.model_dump(exclude_unset=True)
        )

        return await self.db.fetch_one(
            query=UPDATE_PRODUCT_BY_ID_QUERY,
            values=product_update_params.model_dump(),
        )


    async def delete_product_by_id(self, *, id: int) -> int | None:
        product = await self.get_product_by_id(id=id)

        if not product:
            return None

        deleted_id = await self.db.execute(
            query=DELETE_PRODUCT_BY_ID_QUERY, 
            values={"id": id}
        )

        return deleted_id
