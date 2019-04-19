from flask_sqlalchemy import SQLAlchemy
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


db = SQLAlchemy()


def as_dict(instance):
    return {
        c.name: getattr(instance, c.name)
        for c in instance.__table__.columns
    }


class Person(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText(), nullable=False)

    membership_pending = db.Column(db.Boolean, default=False)
    member = db.Column(db.Boolean, default=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    email_valid = db.Column(db.Boolean, default=False)

    date_of_birth = db.Column(db.Date, nullable=True)
    joining_date = db.Column(db.Date, default=date.today, nullable=True)

    user = db.relationship('User', backref='person', lazy='dynamic')


roles = db.Table(
    'roles',
    db.Column('user_id',
              db.Integer,
              db.ForeignKey('user.id'),
              primary_key=True),
    db.Column('role_id',
              db.String(32),
              db.ForeignKey('role.id'),
              primary_key=True))


class Role(db.Model):
    id = db.Column(db.String(32), primary_key=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

    roles = db.relationship('Role',
                            secondary=roles,
                            lazy='subquery',
                            backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
