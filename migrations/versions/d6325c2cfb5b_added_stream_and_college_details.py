"""added stream and college details

Revision ID: d6325c2cfb5b
Revises: acbd336556f2
Create Date: 2023-06-23 22:36:37.035965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6325c2cfb5b'
down_revision = 'acbd336556f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stream',
    sa.Column('stream_id', sa.Integer(), nullable=False),
    sa.Column('stream_name', sa.String(length=255), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['course.course_id'], ),
    sa.PrimaryKeyConstraint('stream_id')
    )
    op.create_table('college',
    sa.Column('college_id', sa.Integer(), nullable=False),
    sa.Column('college_name', sa.String(length=255), nullable=False),
    sa.Column('college_address', sa.String(length=255), nullable=True),
    sa.Column('college_web', sa.String(length=255), nullable=True),
    sa.Column('stream_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stream_id'], ['stream.stream_id'], ),
    sa.PrimaryKeyConstraint('college_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('college')
    op.drop_table('stream')
    # ### end Alembic commands ###
