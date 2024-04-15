"""chat: add page_id column

Revision ID: 1fda63a49965
Revises: 340fc8616938
Create Date: 2024-04-14 20:43:50.230268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fda63a49965'
down_revision: Union[str, None] = '340fc8616938'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Chat', sa.Column('page_id', sa.Integer(), nullable=True, comment='tab id assigned in user level'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Chat', 'page_id')
    # ### end Alembic commands ###
