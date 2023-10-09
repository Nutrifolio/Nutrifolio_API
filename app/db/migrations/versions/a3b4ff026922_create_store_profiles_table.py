"""create_store_profiles_table

Revision ID: a3b4ff026922
Revises: b49d0d1710d7
Create Date: 2023-10-08 20:44:23.783496

"""
from alembic import op
from geoalchemy2 import Geography
import sqlalchemy as sa



# revision identifiers, used by Alembic
revision = 'a3b4ff026922'
down_revision = 'b49d0d1710d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'store_profiles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, unique=True, nullable=False),
        sa.Column('logo_url', sa.String, nullable=True),
        sa.Column('phone_number', sa.NUMERIC, nullable=True),
        sa.Column('address', sa.String, nullable=False),
        sa.Column('lat', sa.Float, nullable=False),
        sa.Column('lng', sa.Float, nullable=False),
        sa.Column('location', Geography('POINT', srid=4326), nullable=False),
        sa.Column(
            'store_id',
            sa.Integer,
            sa.ForeignKey('stores.id', ondelete='CASCADE', onupdate='CASCADE'),
            unique=True,
            nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table('store_profiles')
