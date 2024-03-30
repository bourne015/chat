"""init db

Revision ID: 8432a66e00f9
Revises:
Create Date: 2024-03-28 10:59:32.304663

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8432a66e00f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
        'User',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50)),
        sa.Column('email', sa.String(50), nullable=False),
        sa.Column('phone', sa.String(50)),
        sa.Column('avatar', sa.String()),
        sa.Column('pwd', sa.String(200), nullable=False),
        sa.Column('active', sa.Boolean),
    )
	op.create_table(
        'Chat',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('title', sa.String(50)),
        sa.Column('contents', sa.JSON),
    )



def downgrade() -> None:
    op.drop_table('Chat')
    op.drop_table('User')
