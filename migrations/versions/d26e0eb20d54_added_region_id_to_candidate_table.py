"""added region_id to candidate table

Revision ID: d26e0eb20d54
Revises: 52e3aab34bbc
Create Date: 2018-03-21 22:44:03.931689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd26e0eb20d54'
down_revision = '52e3aab34bbc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('candidates', sa.Column('region_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'candidates', 'regions', ['region_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'candidates', type_='foreignkey')
    op.drop_column('candidates', 'region_id')
    # ### end Alembic commands ###
