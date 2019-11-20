def test_new_user(client):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check if the username and password fields are defined correctly
    """
    from database.models import Person, User, db

    p = Person(name='Alfred Nobel', email='alfred.nobel@tu-dortmund.de')
    u = User(person=p)
    u.set_password('test')

    db.session.add(p, u)
    db.session.commit()

    assert u.person_id == p.id
