"""removed fk from department

Revision ID: 9cc7b90ec4ed
Revises: 8a278c9d3583
Create Date: 2018-03-15 20:48:26.064774

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cc7b90ec4ed'
down_revision = '8a278c9d3583'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organisation', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('responsibilities', sa.Text(), nullable=True),
    sa.Column('region', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organisation'], ['organisation.id'], ),
    sa.ForeignKeyConstraint(['region'], ['regions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('department')
    op.drop_table('role')
    op.create_unique_constraint(None, 'candidates', ['user_id'])
    op.add_column('organisation', sa.Column('parent_dept', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organisation', 'parent_dept')
    op.drop_constraint(None, 'candidates', type_='unique')
    op.create_table('role',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('organisation', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('responsibilities', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('region', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['organisation'], ['organisation.id'], name='role_organisation_fkey'),
    sa.ForeignKeyConstraint(['region'], ['regions.id'], name='role_region_fkey'),
    sa.PrimaryKeyConstraint('id', name='role_pkey')
    )
    op.create_table('department',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('parent_dept', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], ['organisation.id'], name='department_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='department_pkey')
    )
    op.drop_table('roles')
    # ### end Alembic commands ###
