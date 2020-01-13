"""empty message

Revision ID: 392917c0d63f
Revises: aaabaee93687
Create Date: 2020-01-13 13:46:50.916435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '392917c0d63f'
down_revision = 'aaabaee93687'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event', sa.Column('force_tu_mail', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('event', 'force_tu_mail')
