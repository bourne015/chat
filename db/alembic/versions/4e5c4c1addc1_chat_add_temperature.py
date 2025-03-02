"""chat: add temperature

Revision ID: 4e5c4c1addc1
Revises: c907f0418370
Create Date: 2025-03-02 11:41:40.333664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e5c4c1addc1'
down_revision: Union[str, None] = 'c907f0418370'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Chat', sa.Column('temperature', sa.Float(), nullable=True, comment='model temperature'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Chat', 'temperature')
    # ### end Alembic commands ###
