"""update model overtime column date -> o_date

Revision ID: c4965d89892b
Revises: 5661204e3c4e
Create Date: 2024-11-27 22:06:43.218788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4965d89892b'
down_revision: Union[str, None] = '5661204e3c4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('overtimes', sa.Column('o_date', sa.Date(), nullable=False))
    op.drop_column('overtimes', 'date')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('overtimes', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('overtimes', 'o_date')
    # ### end Alembic commands ###
