from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Person(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText(), nullable=False)

    member = db.Column(db.Boolean, default=False)
    member_approved = db.Column(db.Boolean, default=False)

    email = db.Column(db.String(120), unique=True, nullable=False)
    email_valid = db.Column(db.Boolean, default=False)

    date_of_birth = db.Column(db.Date, nullable=True)
    joing_date = db.Column(db.Date, nullable=True)
