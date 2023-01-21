from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import validates
from jsonschema.validators import Draft7Validator
from urllib.parse import quote

from ..models import db


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.Text)
    notify_email = db.Column(db.Text)
    force_tu_mail = db.Column(db.Boolean, default=False)

    def default_shortlink(context):
        """Generates a default shortlink out of the name of the event, by removing spaces and making it URL-safe."""
        if context is not None:
            return quote(context.get_current_parameters()["name"].replace(" ", ""))
        else:
            return ""

    shortlink = db.Column(
        db.Text, default=default_shortlink, nullable=True, unique=True
    )

    max_participants = db.Column(db.Integer)

    registration_open = db.Column(db.Boolean, default=False)
    registration_schema = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)

    @validates("registration_schema")
    def validate_schema(self, key, schema):
        Draft7Validator.check_schema(schema)
        return schema

    def __repr__(self):
        return f"<Event {self.id}: {self.name}>"


class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    event = db.relationship("Event", backref=db.backref("registrations", lazy=True))

    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    person = db.relationship(
        "Person", backref=db.backref("event_registrations", lazy=True)
    )

    status_name = db.Column(
        db.String, db.ForeignKey("registration_status.name"), nullable=False
    )
    status = db.relationship(
        "RegistrationStatus", backref=db.backref("event_registrations", lazy=True)
    )

    data = db.Column(MutableDict.as_mutable(db.JSON))
    timestamp = db.Column(db.DateTime(timezone=True))

    __table_args__ = (
        # a person can only register once for an event
        db.UniqueConstraint("event_id", "person_id", name="unique_person_event"),
    )

    def __repr__(self):
        return f"<EReg {self.id}: P.{self.person_id} for E.{self.event_id}>"


class RegistrationStatus(db.Model):
    name = db.Column(db.String, primary_key=True)

    CONFIRMED = "confirmed"
    PENDING = "pending"
    WAITING = "waitinglist"
    CANCELED = "canceled"
    STATES = (CONFIRMED, PENDING, WAITING, CANCELED)
