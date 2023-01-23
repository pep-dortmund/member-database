"""Add table MembershipStatus and corresponding changes to Person Model

Downgrade below this version is deactivated to prevent loss of membership data.

Revision ID: 02fcfdcb4b37
Revises: 288c44807361
Create Date: 2020-10-25 15:21:23.161567

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02fcfdcb4b37"
down_revision = "288c44807361"
branch_labels = None
depends_on = None


def upgrade():
    # turn of referential integrity checks for foreign keys in sqlite
    # necessary because sqlite does not support renaming, so
    # a new table is created, data copied, old table deleted and new
    # table renamed to the name of the old table.
    # The deletion of the old table is not possible with integrity checks
    # enabled.
    con = op.get_bind()
    if con.engine.name == "sqlite":
        con.execute("PRAGMA foreign_keys = OFF;")

    op.create_table(
        "membership_status",
        sa.Column("id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_membership_status")),
    )
    with op.batch_alter_table("person", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "membership_status_id",
                sa.String,
                sa.ForeignKey("membership_status.id"),
            )
        )
        batch_op.drop_column("member")
        batch_op.drop_column("membership_pending")
