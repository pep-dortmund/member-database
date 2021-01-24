from datetime import date

from .base import db


class Person(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText(), nullable=False)

    membership_status_id = db.Column(
        db.String, db.ForeignKey('membership_status.id'),
    )
    membership_status = db.relationship(
        'MembershipStatus', backref='persons', lazy='subquery'
    )

    membership_type_id = db.Column(
        db.String, db.ForeignKey('membership_type.id'),
    )
    membership_type = db.relationship(
        'MembershipType', backref='persons', lazy='subquery'
    )

    tu_status_id = db.Column(db.Integer, db.ForeignKey('tu_status.id'))
    tu_status = db.relationship(
        'TUStatus', backref='persons', lazy='subquery'
    )

    email = db.Column(db.String(120), unique=True, nullable=False)
    email_valid = db.Column(db.Boolean, default=False)

    date_of_birth = db.Column(db.Date, nullable=True)
    joining_date = db.Column(db.Date, default=None, nullable=True)

    def __repr__(self):
        return f'<Person {self.id}: {self.name}>'


class TUStatus(db.Model):
    STUDENT = 'Student*in'
    PHD = 'Doktorand*in'
    ALUMNI = 'Alumnus/Alumna'
    STAFF = 'Mitarbeiter*in / Lehrende'
    OTHER = 'Sonstiges'

    STATES = (
        STUDENT,
        PHD,
        ALUMNI,
        STAFF,
        OTHER,
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class MembershipStatus(db.Model):
    id = db.Column(db.String, primary_key=True)

    EMAIL_UNVERIFIED = 'email_unverified'
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    DENIED = 'denied'
    CANCELED = 'canceled'

    STATES = (
        EMAIL_UNVERIFIED,
        PENDING,
        CONFIRMED,
        DENIED,
        CANCELED,
    )


class MembershipType(db.Model):
    id = db.Column(db.String, primary_key=True)

    ORDENTLICH = 'ordentlich'
    AUSSERORDENTLICH = 'ausserordentlich'

    TYPES = (
    ORDENTLICH,
    AUSSERORDENTLICH,
    )

