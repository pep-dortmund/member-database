"""Add footer to Event

Revision ID: 0151da823114
Revises: 6799f436c654
Create Date: 2023-02-07 21:40:58.296724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0151da823114'
down_revision = '6799f436c654'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('footer', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('footer')

    # ### end Alembic commands ###
