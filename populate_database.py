from member_database import create_app, db
from member_database.authentication import ACCESS_LEVELS, AccessLevel, Role, User
from member_database.events.common_schemata import ABSOLVENTENFEIER, TOOLBOX
from member_database.events.models import Event
from member_database.models import Person

app = create_app()
app.app_context().push()

if Person.query.filter_by(email="admin@pep-dortmund.org").first() is None:
    print("Creating user admin")
    p = Person(name="Albert Admin", email="admin@pep-dortmund.org")
    u = User(person=p, username="admin")
    u.set_password("testdb")

    access_levels = [db.session.get(AccessLevel, level) for level in ACCESS_LEVELS]
    r = Role(id="admin", access_levels=access_levels)
    u.roles.append(r)

    db.session.add(p, u)
    db.session.commit()
else:
    print("user already exists")


if Event.query.first() is None:
    print("creating event")
    event = Event(
        name="Toolbox Workshop 2019",
        description="Toller Workshop",
        max_participants=1,
        registration_open=True,
        registration_schema=TOOLBOX,
    )
    db.session.add(event)
    db.session.commit()
else:
    print("Event already exists")

if Event.query.filter_by(name="Absolventenfeier 2019").first() is None:
    print("Adding ABSOLVENTENFEIER")
    event = Event(
        name="Absolventenfeier 2019",
        description="Absolventenfeier des Jahres 2019",
        registration_open=True,
        registration_schema=ABSOLVENTENFEIER,
    )
    db.session.add(event)
    db.session.commit()
