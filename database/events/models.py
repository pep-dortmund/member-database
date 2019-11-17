from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import validates
from jsonschema import validate

from ..models import db
from .common_schemata import META_SCHEMA


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)

    max_participants = db.Column(db.Integer)

    registration_open = db.Column(db.Boolean, default=False)
    registration_schema = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)

    @validates('registration_schema')
    def validate_schema(self, key, schema):
        validate(schema, META_SCHEMA)
        return schema


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('registrations', lazy=True))

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship(
        'Person', backref=db.backref('event_registrations', lazy=True)
    )

    status_name = db.Column(db.String, db.ForeignKey('registration_status.name'))
    status = db.relationship('RegistrationStatus', backref=db.backref('status', lazy=True))

    data = db.Column(MutableDict.as_mutable(db.JSON))
    timestamp = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        # a person can only register once for an event
        db.UniqueConstraint('event_id', 'person_id', name='unique_person_event'),
    )


class RegistrationStatus(db.Model):
    name = db.Column(db.String, primary_key=True)
