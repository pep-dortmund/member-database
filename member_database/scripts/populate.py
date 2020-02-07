from .. import create_app
from ..models import db, RegistrationStatus
from ..utils import get_or_create


def main():
    app = create_app()
    with app.app_context():
        get_or_create(RegistrationStatus, name='pending')
        get_or_create(RegistrationStatus, name='registered')
        get_or_create(RegistrationStatus, name='waiting')
        get_or_create(RegistrationStatus, name='canceled')
        db.session.commit()


if __name__ == '__main__':
    main()
