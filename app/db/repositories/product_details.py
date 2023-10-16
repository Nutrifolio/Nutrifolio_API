from app.db.repositories.base import BaseRepository
from app.models.product_details import ProductDetailsCreate, ProductDetailsInDB


GET_PRODUCT_DETAILS_BY_PRODUCT_ID_QUERY = """
    SELECT id, calories, protein, carbs, fiber, sugars, fat, saturated_fat, product_id
    FROM product_details
    WHERE product_id = :product_id;
"""

CREATE_PRODUCT_DETAILS_QUERY = """
    INSERT INTO product_details (
        calories, protein, carbs, fiber, sugars, fat, saturated_fat, product_id
    )
    VALUES (
        :calories, :protein, :carbs, :fiber, :sugars, :fat, :saturated_fat, :product_id
    )
    RETURNING
        id, calories, protein, carbs, fiber, sugars, fat, saturated_fat, product_id;
"""


class ProductDetailsRepository(BaseRepository):
    """"
    All database actions associated with the ProductDetails resource
    """

    async def get_product_details_by_product_id(
        self, *, product_id: int
    ) -> ProductDetailsInDB:
        product_details_record = await self.db.fetch_one(
            query=GET_PRODUCT_DETAILS_BY_PRODUCT_ID_QUERY, 
            values={"product_id": product_id}
        )

        if not product_details_record:
            return None

        return ProductDetailsInDB(**product_details_record)


    async def create_product_details(
        self, *, new_product_details: ProductDetailsCreate
    ) -> ProductDetailsInDB:
        product_details_record = await self.db.fetch_one(
            query=CREATE_PRODUCT_DETAILS_QUERY, 
            values=new_product_details.model_dump()
        )

        return ProductDetailsInDB(**product_details_record)
