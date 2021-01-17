import pytest
import tempfile


@pytest.fixture(scope='session')
def app():
    from config import TestingConfig
    from member_database import create_app

    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope='session')
def client(app):
    from member_database import db

    with tempfile.NamedTemporaryFile(suffix='.sqlite', prefix='db_testing') as f:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + f.name

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client


@pytest.fixture(scope='session')
def admin_user(client):
    from member_database.models import Person, User, Role, AccessLevel, db
    from member_database.utils import get_or_create

    admin = Role(id='admin', access_levels=[
        get_or_create(AccessLevel, id='member_management')[0],
    ])

    p = Person(name='Richard Feynman', email='rfeynman@example.org')
    u = User(person=p, username='rfeynman', roles=[admin])

    # store clear text password in object so we can use it in the tests
    u.password = 'bongos'
    u.login_data = dict(
        user_or_email=u.username,
        password=u.password
    )
    u.set_password(u.password)

    db.session.add(u)
    db.session.commit()

    return u
