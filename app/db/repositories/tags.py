from typing import List
from app.db.repositories.base import BaseRepository
from app.models.tags import TagInDB


GET_TAGS_QUERY = """
    SELECT id, label, description
    FROM tags;
"""

GET_TAG_BY_ID_QUERY = """
    SELECT id, label, description
    FROM tags
    WHERE id = :id;
"""

GET_TAGS_FOR_PRODUCT_BY_PRODUCT_ID_QUERY = """
    SELECT t.id, t.label, t.description
    FROM tags AS t
        INNER JOIN product_tags AS pt ON t.id = pt.tag_id
    WHERE pt.product_id = :product_id;
"""


class TagsRepository(BaseRepository):
    """"
    All database actions associated with the Tag resource
    """

    async def get_all_tags(self) -> List[TagInDB]:
        tag_records = await self.db.fetch_all(query=GET_TAGS_QUERY)

        return [
            TagInDB(**tag_record)
            for tag_record in tag_records
        ]


    async def get_tag_by_id(self, *, id: int) -> TagInDB:
        tag_record = await self.db.fetch_one(
            query=GET_TAG_BY_ID_QUERY, values={"id": id}
        )

        if not tag_record:
            return None

        return TagInDB(**tag_record)


    async def get_tags_for_product_by_product_id(
        self, *, product_id: int
    ) -> list[TagInDB]:
        tag_records = await self.db.fetch_all(
            query=GET_TAGS_FOR_PRODUCT_BY_PRODUCT_ID_QUERY, 
            values={"product_id": product_id}
        )

        return [
            TagInDB(**tag_record)
            for tag_record in tag_records
        ]
