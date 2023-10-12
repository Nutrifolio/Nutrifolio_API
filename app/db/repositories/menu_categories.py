from typing import List
from app.db.repositories.base import BaseRepository
from app.models.menu_categories import MenuCategoryInDB


GET_MENU_CATEGORY_BY_ID_QUERY = """
    SELECT id, label, description
    FROM menu_categories
    WHERE id = :id;
"""


class MenuCategoriesRepository(BaseRepository):
    """"
    All database actions associated with the MenuCategory resource
    """

    async def get_menu_category_by_id(self, *, id: int) -> MenuCategoryInDB:
        menu_category_record = await self.db.fetch_one(
            query=GET_MENU_CATEGORY_BY_ID_QUERY, values={"id": id}
        )

        if not menu_category_record:
            return None

        return MenuCategoryInDB(**menu_category_record)
