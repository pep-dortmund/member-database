"""empty message

Revision ID: 392917c0d63f
Revises: aaabaee93687
Create Date: 2020-01-13 13:46:50.916435

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "392917c0d63f"
down_revision = "aaabaee93687"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("event") as bop:
        bop.add_column(sa.Column("force_tu_mail", sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table("event") as bop:
        bop.drop_column("force_tu_mail")
