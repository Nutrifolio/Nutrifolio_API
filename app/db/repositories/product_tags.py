from app.db.repositories.base import BaseRepository
from app.models.product_tags import ProductTagCreate, ProductTagInDB


GET_PRODUCT_TAGS_BY_PRODUCT_ID_QUERY = """
    SELECT product_id, tag_id
    FROM product_tags
    WHERE product_id = :product_id;
"""


CREATE_PRODUCT_TAG_QUERY = """
    INSERT INTO product_tags (product_id, tag_id)
    VALUES (:product_id, :tag_id)
    RETURNING product_id, tag_id;
"""


class ProductTagsRepository(BaseRepository):
    """"
    All database actions associated with the ProductTags resource
    """

    async def get_product_tags_by_product_id(
        self, *, product_id: int
    ) -> list[ProductTagInDB]:
        product_tag_records = await self.db.fetch_all(
            query=GET_PRODUCT_TAGS_BY_PRODUCT_ID_QUERY, 
            values={"product_id": product_id}
        )

        return [
            ProductTagInDB(**product_tag_record)
            for product_tag_record in product_tag_records
        ]


    async def create_product_tag(
        self, *, new_product_tag: ProductTagCreate
    ) -> ProductTagInDB:
        product_tag_record = await self.db.fetch_one(
            query=CREATE_PRODUCT_TAG_QUERY, 
            values=new_product_tag.model_dump()
        )

        return ProductTagInDB(**product_tag_record)
