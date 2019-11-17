import pytest

@pytest.fixture(scope='module')
def new_user():
    from database.models import Person, User

    person = Person(name='Alfred Nobel', email='alfred@tu-dortmund.de')
    user = User(person=person, username='anobel')
    user.set_password('testpw')
    return user

@pytest.fixture(scope='module')
def test_client():
    from database import app

    app.config.from_object('config.TestingConfig')

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

#@pytest.fixture(scope='module')
#def init_database():
#    db.create_all()
#
#    # Insert user data
#    person1 = Person(name='Alfred Nobel', email='alfred@tu-dortmund.de')
#    user1 = User(person=person1, username='anobel')
#    person2 = Person(name='Nikola Tesla', email='nikola@tu-dortmund.de')
#    user2 = User(person=person2, username='ntesla')
#    db.session.add(user1)
#    db.session.add(user2)
#
#    # Commit the changes for the users
#    db.session.commit()
#
#    yield db  # this is where the testing happens!
#
#    db.drop_all()
