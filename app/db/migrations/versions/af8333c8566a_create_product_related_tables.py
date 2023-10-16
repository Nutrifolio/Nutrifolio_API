"""create_product_related_tables

Revision ID: af8333c8566a
Revises: a3b4ff026922
Create Date: 2023-10-11 12:26:44.633025

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import Table


# revision identifiers, used by Alembic
revision = 'af8333c8566a'
down_revision = 'a3b4ff026922'
branch_labels = None
depends_on = None


def create_menu_categories_table() -> Table:
    menu_categories_table = op.create_table(
        "menu_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String, unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )
    return menu_categories_table


def initialize_menu_categories_table(menu_categories_table: Table) -> None:
    op.bulk_insert(
        menu_categories_table,
        [
            {'id': 1, 'label': 'Sandwiches'},
            {'id': 2, 'label': 'Salads'},
        ]
    )


def create_tags_table() -> Table:
    tags_table = op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String, unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )
    return tags_table


def initialize_tags_table(tags_table: Table) -> None:
    op.bulk_insert(
        tags_table,
        [
            {'id': 1, 'label': 'Vegan'},
            {'id': 2, 'label': 'Vegetarian'},
            {'id': 3, 'label': 'Pescatarian'},
            {'id': 4, 'label': 'High Protein'},
            {'id': 5, 'label': 'Low Fat'},
            {'id': 6, 'label': 'Sugar Free'},
            {'id': 7, 'label': 'Gluten Free'},
            {'id': 8, 'label': 'Lactose Free'}
        ]
    )


def create_products_table() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("image_url", sa.String, nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("view_count", sa.Integer, server_default="0", nullable=False),
        sa.Column(
            "has_details",
            sa.Boolean,
            server_default=sa.sql.false(),
            nullable=False
        ),
        sa.Column(
            "is_public",
            sa.Boolean,
            server_default=sa.sql.false(),
            nullable=False
        ),
        sa.Column(
            "store_id",
            sa.Integer,
            sa.ForeignKey("stores.id", ondelete="CASCADE", onupdate="CASCADE"),
            index=True,
            nullable=False
        ),
        sa.UniqueConstraint("name", "store_id", name="unique_product_name_per_store")
    )


def create_product_details_table() -> None:
    op.create_table('product_details',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('calories', sa.Integer, nullable=True),
        sa.Column('protein', sa.Float, nullable=True),
        sa.Column('carbs', sa.Float, nullable=True),
        sa.Column('fiber', sa.Float, nullable=True),
        sa.Column('sugars', sa.Float, nullable=True),
        sa.Column('fat', sa.Float, nullable=True),
        sa.Column('saturated_fat', sa.Float, nullable=True),
        sa.Column(
            'product_id',
            sa.Integer,
            sa.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
            unique=True,
            nullable=False
        ),
    )


def create_product_menu_categories_table() -> None:
    op.create_table('product_menu_categories',
        sa.Column(
            'product_id',
            sa.Integer,
            sa.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False
        ),
        sa.Column(
            'menu_category_id',
            sa.Integer,
            sa.ForeignKey("menu_categories.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('product_id', 'menu_category_id')
    )


def create_product_tags_table() -> None:
    op.create_table('product_tags',
        sa.Column(
            'product_id',
            sa.Integer,
            sa.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False
        ),
        sa.Column(
            'tag_id',
            sa.Integer,
            sa.ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('product_id', 'tag_id')
    )


def upgrade() -> None:
    menu_categories_table = create_menu_categories_table()
    initialize_menu_categories_table(menu_categories_table)
    tags_table = create_tags_table()
    initialize_tags_table(tags_table)
    create_products_table()
    create_product_details_table()
    create_product_menu_categories_table()
    create_product_tags_table()


def downgrade() -> None:
    op.drop_table("product_tags")
    op.drop_table("product_menu_categories")
    op.drop_table("product_details")
    op.drop_table("products")
    op.drop_table("tags")
    op.drop_table("menu_categories")
