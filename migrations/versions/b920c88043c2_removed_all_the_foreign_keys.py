"""removed all the foreign keys!

Revision ID: b920c88043c2
Revises: 9cc7b90ec4ed
Create Date: 2018-03-15 21:10:04.215617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b920c88043c2'
down_revision = '9cc7b90ec4ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('candidates')
    op.drop_table('scheme_leaders')
    op.drop_table('activity_managers')
    op.drop_table('cohort_leaders')
    op.add_column('users', sa.Column('line_manager_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('organisation', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('specialism', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('staff_number', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'users', ['staff_number'])
    op.create_foreign_key(None, 'users', 'organisation', ['organisation'], ['id'])
    op.create_foreign_key(None, 'users', 'specialisms', ['specialism'], ['id'])
    op.create_foreign_key(None, 'users', 'users', ['line_manager_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'staff_number')
    op.drop_column('users', 'specialism')
    op.drop_column('users', 'organisation')
    op.drop_column('users', 'line_manager_id')
    op.create_table('cohort_leaders',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='cohort_leaders_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='cohort_leaders_pkey')
    )
    op.create_table('activity_managers',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('organisation', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='activity_managers_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organisation'], ['organisation.id'], name='activity_managers_organisation_fkey'),
    sa.PrimaryKeyConstraint('id', name='activity_managers_pkey')
    )
    op.create_table('scheme_leaders',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('specialism', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='scheme_leaders_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['specialism'], ['specialisms.id'], name='scheme_leaders_specialism_fkey'),
    sa.PrimaryKeyConstraint('id', name='scheme_leaders_pkey')
    )
    op.create_table('candidates',
    sa.Column('staff_number', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('specialism', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('line_manager_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['line_manager_id'], ['users.id'], name='candidates_line_manager_id_fkey'),
    sa.ForeignKeyConstraint(['specialism'], ['specialisms.id'], name='candidates_specialism_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='candidates_user_id_fkey'),
    sa.UniqueConstraint('staff_number', name='candidates_staff_number_key'),
    sa.UniqueConstraint('user_id', name='candidates_user_id_key')
    )
    # ### end Alembic commands ###
