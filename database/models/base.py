from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def as_dict(instance):
    ''' Transform a model instance into a dict '''
    return {
        c.name: getattr(instance, c.name)
        for c in instance.__table__.columns
    }
