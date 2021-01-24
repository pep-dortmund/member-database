from member_database import create_app, db
from member_database.models import Person
from member_database.authentication import User, Role, AccessLevel
from member_database.events.models import Event, RegistrationStatus
from member_database.events.common_schemata import ABSOLVENTENFEIER, TOOLBOX
from member_database.utils import get_or_create

app = create_app()
app.app_context().push()

if Person.query.filter_by(email='max.noethe@t-online.de').first() is None:
    print('Creating user mnoethe')
    p = Person(name='Maximilian Nöthe', email='max.noethe@t-online.de')
    u = User(person=p, username='mnoethe')
    u.set_password('testdb')

    r = Role(id='workshop')
    r.access_levels.append(get_or_create(AccessLevel, id='get_participants')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='event_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='role_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='access_level_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='event_registration_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='person_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='user_admin')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='write_email')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='member_management')[0])
    r.access_levels.append(get_or_create(AccessLevel, id='get_members')[0])
    u.roles.append(r)

    db.session.add(p, u)
    db.session.commit()
else:
    print('user already exists')


if Event.query.first() is None:
    print('creating event')
    event = Event(
        name='Toolbox Workshop 2019',
        description='Toller Workshop',
        max_participants=1,
        registration_open=True,
        registration_schema=TOOLBOX,
    )
    db.session.add(event)
    db.session.commit()
else:
    print('Event already exists')

if Event.query.filter_by(name='Absolventenfeier 2019').first() is None:
    print('Adding ABSOLVENTENFEIER')
    event = Event(
        name='Absolventenfeier 2019',
        description='Absolventenfeier des Jahres 2019',
        registration_open=True,
        registration_schema=ABSOLVENTENFEIER,
    )
    db.session.add(event)
    db.session.commit()


print('Add registration stati')
for status in ['pending', 'confirmed', 'canceled', 'waitinglist']:
    get_or_create(RegistrationStatus, name=status)
db.session.commit()
