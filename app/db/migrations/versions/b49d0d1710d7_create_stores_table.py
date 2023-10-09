"""create_stores_table

Revision ID: b49d0d1710d7
Revises: db6d85632755
Create Date: 2023-10-08 18:35:35.238688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'b49d0d1710d7'
down_revision = 'db6d85632755'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'stores',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('is_verified', sa.Boolean, server_default='false', nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_table('stores')
