from database import app, db
from database.models import Person, User, Event, RegistrationStatus
from database.utils import get_or_create

app.app_context().push()

if Person.query.filter_by(name='Maximilian Nöthe').first() is None:
    print('Creating user mnoethe')
    p = Person(name='Maximilian Nöthe', email='max.noethe@t-online.de')
    u = User(person=p, username='mnoethe')
    u.set_password('testdb')

    db.session.add(p, u)
    db.session.commit()
else:
    print('user already exists')


if Event.query.first() is None:
    print('creating event')
    event = Event(
        name='Absolventenfeier 2019',
        description='Tolle Absolventenfeier',
        registration_open=True,
        registration_schema={
            'type': 'object',
            'properties': {
                'semester': { 'type': 'integer', 'label': 'Semester'},
                'vegan': {'type': 'boolean', 'label': 'Vegan'},
                'allergies': {'type': 'string', 'label': 'Unverträglichkeiten oder Allergien'},
                'degree': {
                    'type': 'string',
                    'label': 'Abschluss',
                    'enum': ['Bachelor', 'Master', 'Promotion'],
                },
            },
            'required': ['semester', 'degree']
        },
    )
    db.session.add(event)
    db.session.commit()
else:
    print('Event already exists')


print('Add registration stati')
for status in ['pending', 'confirmed', 'canceled', 'waitinglist']:
    get_or_create(RegistrationStatus, name=status)
db.session.commit()
