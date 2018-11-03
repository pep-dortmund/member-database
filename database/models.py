from flask_sqlalchemy import SQLAlchemy
from datetime import date


db = SQLAlchemy()


def as_dict(instance):
    return {
        c.name: getattr(instance, c.name)
        for c in instance.__table__.columns
    }


class Person(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText(), nullable=False)

    member = db.Column(db.Boolean, default=False)
    member_approved = db.Column(db.Boolean, default=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    email_valid = db.Column(db.Boolean, default=False)

    date_of_birth = db.Column(db.Date, nullable=True)
    joining_date = db.Column(db.Date, default=date.today, nullable=True)
