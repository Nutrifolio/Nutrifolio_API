from typing import List
from app.db.repositories.base import BaseRepository
from app.models.menu_categories import MenuCategoryInDB


GET_MENU_CATEGORY_BY_ID_QUERY = """
    SELECT id, label, description
    FROM menu_categories
    WHERE id = :id;
"""

GET_MENU_CATEGORIES_FOR_PRODUCT_BY_PRODUCT_ID = """
    SELECT mc.id, mc.label, mc.description
    FROM menu_categories AS mc
        INNER JOIN product_menu_categories AS pmc ON mc.id = pmc.menu_category_id
    WHERE pmc.product_id = :product_id;
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


    async def get_menu_categories_for_product_by_product_id(
        self, *, product_id: int
    ) -> list[MenuCategoryInDB]:
        menu_category_records = await self.db.fetch_all(
            query=GET_MENU_CATEGORIES_FOR_PRODUCT_BY_PRODUCT_ID, 
            values={"product_id": product_id}
        )

        return [
            MenuCategoryInDB(**menu_category_record) 
            for menu_category_record in menu_category_records
        ]
