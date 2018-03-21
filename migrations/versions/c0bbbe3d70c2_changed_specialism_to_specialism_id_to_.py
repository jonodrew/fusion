"""changed specialism to specialism_id to allow for specialism relationship

Revision ID: c0bbbe3d70c2
Revises: c9501a8e1a2d
Create Date: 2018-03-18 14:46:32.922921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0bbbe3d70c2'
down_revision = 'c9501a8e1a2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('candidates', sa.Column('specialism_id', sa.Integer(), nullable=True))
    op.drop_constraint('candidates_specialism_fkey', 'candidates', type_='foreignkey')
    op.create_foreign_key(None, 'candidates', 'specialisms', ['specialism_id'], ['id'])
    op.drop_column('candidates', 'specialism')
    op.add_column('users', sa.Column('specialism_id', sa.Integer(), nullable=True))
    op.drop_constraint('users_specialism_fkey', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'specialisms', ['specialism_id'], ['id'])
    op.drop_column('users', 'specialism')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('specialism', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users_specialism_fkey', 'users', 'specialisms', ['specialism'], ['id'])
    op.drop_column('users', 'specialism_id')
    op.add_column('candidates', sa.Column('specialism', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'candidates', type_='foreignkey')
    op.create_foreign_key('candidates_specialism_fkey', 'candidates', 'specialisms', ['specialism'], ['id'])
    op.drop_column('candidates', 'specialism_id')
    # ### end Alembic commands ###