import pytest
from member_database import (
    init_authentication_database,
    init_main_database,
    init_event_database,
)


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    return tmp_path_factory.mktemp("db_") / "db_testing.sqlite"


@pytest.fixture(scope="session")
def app(db_path):
    from config import TestingConfig
    from member_database import create_app

    TestingConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope="session")
def client(app):
    from member_database import db

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            init_authentication_database()
            init_main_database()
            init_event_database()
            yield client


@pytest.fixture(scope="session")
def test_person(client):
    from member_database.models import Person, db

    p = Person(name="Richard Feynman", email="rfeynman@example.org")

    db.session.add(p)
    db.session.commit()

    return p


@pytest.fixture(scope="session")
def admin_user(client, test_person):
    from member_database.models import Person, db
    from member_database.authentication import User, Role, AccessLevel
    from member_database.utils import get_or_create

    member_management, _ = get_or_create(AccessLevel, id="member_management")
    admin = Role(
        id="admin",
        access_levels=[member_management],
    )
    db.session.add(admin)

    u = User(person=test_person, username="rfeynman", roles=[admin])

    # store clear text password in object so we can use it in the tests
    u.password = "bongos"
    u.login_data = dict(user_or_email=u.username, password=u.password)
    u.set_password(u.password)

    db.session.add(u)
    db.session.commit()

    return u
