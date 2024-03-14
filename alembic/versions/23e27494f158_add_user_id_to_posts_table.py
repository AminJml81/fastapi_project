"""add user_id to posts table

Revision ID: 23e27494f158
Revises: 18fa63dc2321
Create Date: 2024-03-14 16:40:09.182842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23e27494f158'
down_revision: Union[str, None] = '18fa63dc2321'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column("user_id", sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'),
                                     nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'user_id')
