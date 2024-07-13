"""change prompts to instructions

Revision ID: 81b8ed10da56
Revises: 81dcbc7e2cfc
Create Date: 2024-07-13 05:44:32.750195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81b8ed10da56'
down_revision: Union[str, None] = '81dcbc7e2cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('Bot', 'prompts', new_column_name='instructions')


def downgrade() -> None:
    op.alter_column('Bot', 'instructions', new_column_name='prompts')
