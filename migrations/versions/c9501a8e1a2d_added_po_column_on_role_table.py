"""added po column on role table

Revision ID: c9501a8e1a2d
Revises: cb037c56c8d5
Create Date: 2018-03-17 17:13:34.144022

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9501a8e1a2d'
down_revision = 'cb037c56c8d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('private_office', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'private_office')
    # ### end Alembic commands ###