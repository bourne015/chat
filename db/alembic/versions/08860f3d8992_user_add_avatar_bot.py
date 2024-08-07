"""user: add avatar_bot

Revision ID: 08860f3d8992
Revises: 81b8ed10da56
Create Date: 2024-07-18 07:49:00.301101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08860f3d8992'
down_revision: Union[str, None] = '81b8ed10da56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Bot', 'instructions',
               existing_type=sa.VARCHAR(),
               comment='bot instructions',
               existing_comment='bot prompts',
               existing_nullable=False)
    op.add_column('User', sa.Column('avatar_bot', sa.String(), nullable=True, comment='bot avatar'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'avatar_bot')
    op.alter_column('Bot', 'instructions',
               existing_type=sa.VARCHAR(),
               comment='bot prompts',
               existing_comment='bot instructions',
               existing_nullable=False)
    # ### end Alembic commands ###
