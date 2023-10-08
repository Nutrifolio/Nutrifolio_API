"""create_users_table

Revision ID: db6d85632755
Revises: 84b7af65d70e
Create Date: 2023-10-05 14:17:12.744015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'db6d85632755'
down_revision = '84b7af65d70e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_table('users')
