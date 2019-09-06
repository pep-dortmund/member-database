from database import app
from database.models import db, RegistrationStatus
from ..utils import get_or_create


def main():
    with app.app_context():
        get_or_create(RegistrationStatus, name='pending')
        get_or_create(RegistrationStatus, name='registered')
        get_or_create(RegistrationStatus, name='waiting')
        get_or_create(RegistrationStatus, name='canceled')
        db.session.commit()


if __name__ == '__main__':
    main()
