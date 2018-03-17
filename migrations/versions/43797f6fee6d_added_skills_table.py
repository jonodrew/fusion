"""added skills table

Revision ID: 43797f6fee6d
Revises: fa6852869418
Create Date: 2018-03-17 13:12:53.457302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43797f6fee6d'
down_revision = 'fa6852869418'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('skills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('specialism', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['specialism'], ['specialisms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_id'), 'skills', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_skills_id'), table_name='skills')
    op.drop_table('skills')
    # ### end Alembic commands ###
