"""added course

Revision ID: acbd336556f2
Revises: 77743a3ec5df
Create Date: 2023-06-23 00:48:35.143231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acbd336556f2'
down_revision = '77743a3ec5df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.Column('course_name', sa.String(length=255), nullable=False),
    sa.Column('content', sa.String(length=255), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('course_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('course')
    # ### end Alembic commands ###