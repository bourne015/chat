"""user: add credit column

Revision ID: 340fc8616938
Revises: a3e37810376f
Create Date: 2024-04-11 16:21:59.744403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '340fc8616938'
down_revision: Union[str, None] = 'a3e37810376f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('User', sa.Column('credit', sa.Float(), nullable=True, comment='credit balance'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'credit')
    # ### end Alembic commands ###