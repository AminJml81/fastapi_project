"""create posts table with id, title, content column

Revision ID: 8d90a799c1ca
Revises: 
Create Date: 2024-03-13 15:36:15.901543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d90a799c1ca'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('posts', sa.Column('id', sa.Integer, nullable=False, primary_key=True)
                    , sa.Column('title', sa.String, nullable=False)
                    , sa.Column('content', sa.String, nullable=False))


def downgrade() -> None:
    op.drop_table('posts')
