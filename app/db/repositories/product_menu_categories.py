from app.db.repositories.base import BaseRepository
from app.models.product_menu_categories import ProductMenuCategoryCreate, ProductMenuCategoryInDB


GET_PRODUCT_MENU_CATEGORIES_BY_PRODUCT_ID_QUERY = """
    SELECT product_id, menu_category_id
    FROM product_menu_categories
    WHERE product_id = :product_id;
"""

CREATE_PRODUCT_MENU_CATEGORY_QUERY = """
    INSERT INTO product_menu_categories (product_id, menu_category_id)
    VALUES (:product_id, :menu_category_id)
    RETURNING product_id, menu_category_id;
"""


class ProductMenuCategoriesRepository(BaseRepository):
    """"
    All database actions associated with the ProductMenuCategories resource
    """


    async def get_product_menu_categories_by_product_id(
        self, *, product_id: int
    ) -> list[ProductMenuCategoryInDB]:
        product_menu_category_records = await self.db.fetch_all(
            query=GET_PRODUCT_MENU_CATEGORIES_BY_PRODUCT_ID_QUERY, 
            values={"product_id": product_id}
        )

        return [
            ProductMenuCategoryInDB(**product_menu_category_record) 
            for product_menu_category_record in product_menu_category_records
        ]


    async def create_product_menu_category(
        self, *, new_product_menu_category: ProductMenuCategoryCreate
    ) -> ProductMenuCategoryInDB:
        product_menu_category_record = await self.db.fetch_one(
            query=CREATE_PRODUCT_MENU_CATEGORY_QUERY, 
            values=new_product_menu_category.model_dump()
        )

        return ProductMenuCategoryInDB(**product_menu_category_record)
