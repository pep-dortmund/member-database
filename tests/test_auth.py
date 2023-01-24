import pytest
import re

OLD_PW = "test"
NEW_PW = "foo"


def test_new_user(client):
    """
    Check if we can create a new user and set its password.
    """
    from member_database.models import Person, db
    from member_database.authentication import User

    p = Person(name="Alfred Nobel", email="alfred.nobel@tu-dortmund.de")
    u = User(person=p)
    u.set_password("test")

    db.session.add(p, u)
    db.session.commit()

    assert u.person_id == p.id


@pytest.fixture(scope="module")
def test_user():
    from member_database.models import Person, db
    from member_database.authentication import User

    p = Person(name="Albert Einstein", email="albert.einstein@tu-dortmund.de")
    u = User(person=p, username="aeinstein")
    u.set_password(OLD_PW)

    db.session.add(p, u)
    db.session.commit()

    return u


@pytest.fixture(scope="module")
def test_user2():
    from member_database.models import Person, db
    from member_database.authentication import User

    p = Person(name="Marie Curie", email="marie.curie@tu-dortmund.de")
    u = User(person=p, username="mcurie")

    db.session.add(p, u)
    db.session.commit()

    return u


def test_home(client):
    """
    Check if the index delivers a valid response
    """
    response = client.get("/")
    assert response.status_code == 200


def test_login(client):
    """
    Check if the login page delivers a valid response
    """
    response = client.get("/login/")
    assert response.status_code == 200


def test_password_reset(client, test_user):
    from member_database.mail import mail

    assert test_user.check_password(OLD_PW)

    with mail.record_messages() as outbox:
        ret = client.post(
            "/password_reset/",
            data={"user_or_email": test_user.username},
            follow_redirects=True,
        )

        # check message was flashed
        assert "Password reset email sent" in ret.data.decode("utf-8")

    # find reset link
    assert len(outbox) == 1
    m = re.search(r"http(s)?:\/\/.*password_reset\/.*", outbox[0].body)
    assert m

    # change password
    ret = client.post(
        m.group(0),
        data={"new_password": NEW_PW, "confirm": NEW_PW},
        follow_redirects=True,
    )

    assert test_user.check_password(NEW_PW)
    assert not test_user.check_password(OLD_PW)

    # unknown user should give a flashed message
    ret = client.post(
        "/password_reset/",
        data={"user_or_email": "non_existent_user"},
        follow_redirects=True,
    )
    assert "Unknown username or email" in ret.data.decode("utf-8")


def test_get_user(test_user, test_user2):
    from member_database.authentication import get_user_by_name_or_email

    assert get_user_by_name_or_email(test_user.username).id == test_user.id
    assert get_user_by_name_or_email(test_user.person.email).id == test_user.id

    assert get_user_by_name_or_email(test_user2.username).id == test_user2.id
    assert get_user_by_name_or_email(test_user2.person.email).id == test_user2.id
