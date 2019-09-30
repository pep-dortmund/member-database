from .base import db
from ..json_forms import validate_form
from sqlalchemy.ext.mutable import MutableDict, MutableList


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)

    registration_open = db.Column(db.Boolean)
    registration_schema = db.Column(MutableList.as_mutable(db.JSON))

    @db.validates('registration_schema')
    def validate_registration_schema(self, key, schema):
        validate_form(schema)
        return schema


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship(
        'Person', backref=db.backref('event_registrations', lazy=True)
    )

    status = db.Column(db.Integer, db.ForeignKey('registration_status.name'))

    data = db.Column(MutableDict.as_mutable(db.JSON))

    __table_args__ = (
        # a person can only register once for an event
        db.UniqueConstraint('event_id', 'person_id', name='unique_person_event'),
    )


class RegistrationStatus(db.Model):
    name = db.Column(db.String, primary_key=True)