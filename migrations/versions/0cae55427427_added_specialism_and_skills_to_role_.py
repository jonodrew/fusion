"""added specialism and skills to Role table

Revision ID: 0cae55427427
Revises: 9a9fe274b225
Create Date: 2018-03-21 20:08:23.080759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cae55427427'
down_revision = '9a9fe274b225'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('skills', sa.JSON(), nullable=True))
    op.add_column('roles', sa.Column('specialism', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'roles', 'specialisms', ['specialism'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roles', type_='foreignkey')
    op.drop_column('roles', 'specialism')
    op.drop_column('roles', 'skills')
    # ### end Alembic commands ###