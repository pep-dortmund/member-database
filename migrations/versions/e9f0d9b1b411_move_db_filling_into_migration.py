"""Move db filling into migration

Revision ID: e9f0d9b1b411
Revises: 94cbf12be25a
Create Date: 2022-11-28 17:53:39.576269

"""
from alembic import op
import sqlalchemy as sa
from member_database.authentication.models import AccessLevel
from member_database.authentication.login import ACCESS_LEVELS

from member_database.models import TUStatus, MembershipStatus, MembershipType
from member_database.events.models import RegistrationStatus



# revision identifiers, used by Alembic.
revision = 'e9f0d9b1b411'
down_revision = '94cbf12be25a'
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(RegistrationStatus.__table__, rows=[
        dict(name='confirmed'),
        dict(name='pending'),
        dict(name='waitinglist'),
        dict(name='canceled'),
    ])

    rows = [dict(name=name) for name in TUStatus.STATES]
    op.bulk_insert(TUStatus.__table__, rows=rows)

    rows = [dict(id=name) for name in MembershipStatus.STATES]
    op.bulk_insert(MembershipStatus.__table__, rows=rows)

    rows = [dict(id=name) for name in MembershipType.TYPES]
    op.bulk_insert(MembershipType.__table__, rows=rows)

    rows = [dict(id=name) for name in ACCESS_LEVELS]
    op.bulk_insert(AccessLevel.__table__, rows=rows)



def downgrade():
    pass
