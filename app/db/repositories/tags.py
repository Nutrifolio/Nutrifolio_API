from typing import List
from app.db.repositories.base import BaseRepository
from app.models.tags import TagInDB


GET_TAG_BY_ID_QUERY = """
    SELECT id, label, description
    FROM tags
    WHERE id = :id;
"""


class TagsRepository(BaseRepository):
    """"
    All database actions associated with the Tag resource
    """

    async def get_tag_by_id(self, *, id: int) -> TagInDB:
        tag_record = await self.db.fetch_one(
            query=GET_TAG_BY_ID_QUERY, values={"id": id}
        )

        if not tag_record:
            return None

        return TagInDB(**tag_record)
