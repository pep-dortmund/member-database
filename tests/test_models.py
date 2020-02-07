def test_new_user(client):
    """
    Check if we can create a new user and set its password.
    """
    from member_database.models import Person, User, db

    p = Person(name='Alfred Nobel', email='alfred.nobel@tu-dortmund.de')
    u = User(person=p)
    u.set_password('test')

    db.session.add(p, u)
    db.session.commit()

    assert u.person_id == p.id
