"""create_main_tables

Revision ID: 84b7af65d70e
Revises: 
Create Date: 2023-09-13 09:09:29.338927

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '84b7af65d70e'
down_revision = None
branch_labels = None
depends_on = None


def create_truncate_tables_function() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION truncate_tables() RETURNS void AS $$
        DECLARE tables_to_truncate CURSOR FOR
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
                AND tablename NOT IN (
                    'alembic_version',
                    'spatial_ref_sys', 
                    'tags',
                    'menu_categories'
                );
        BEGIN
            FOR tbl IN tables_to_truncate LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(tbl.tablename) || ' RESTART IDENTITY CASCADE;';
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def upgrade() -> None:
    create_truncate_tables_function()


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS truncate_tables();")
