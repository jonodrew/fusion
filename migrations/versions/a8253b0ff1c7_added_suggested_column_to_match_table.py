"""added suggested column to match table

Revision ID: a8253b0ff1c7
Revises: 78dc5aa5138f
Create Date: 2018-03-22 22:09:54.612976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8253b0ff1c7'
down_revision = '78dc5aa5138f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('matches', sa.Column('suggested', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('matches', 'suggested')
    # ### end Alembic commands ###