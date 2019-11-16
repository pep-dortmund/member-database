from database import app, db
from database.models import Person, User, Event, RegistrationStatus

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
        registration_schema=[
            {
                'type': 'integer',
                'label': 'Semester',
                'id': 'semester',
                'required': True,
            },
            {
                'type': 'text',
                'label': 'title',
                'id': 'title',
                'required': True,
            },
            {
                'type': 'select',
                'label': 'Abschluss',
                'id': 'degree',
                'options': [
                    {'value': 'bachelor', 'label': 'Bachelor'},
                    {'value': 'master', 'label': 'Master'},
                    {'value': 'phd', 'label': 'Promotion'},
                ]
            }
        ]
    )
    db.session.add(event)
    db.session.commit()
else:
    print('Event already exists')


if not RegistrationStatus.query.first():
    print('Add registration stati')
    for status in ['pending', 'registered', 'canceled', 'waitinglist']:
        db.session.add(RegistrationStatus(name=status))
    db.session.commit()

