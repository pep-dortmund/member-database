from flask_sqlalchemy import SQLAlchemy
import json
import decimal


class DecimalEncoder(json.JSONEncoder):
    """ Need to encode decimal objects from the html5.decimalinput fields
    See https://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal-object
    and https://stackoverflow.com/questions/36438052/using-a-custom-json-encoder-for-sqlalchemys-postgresql-jsonb-implementation/36438671
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def dumps(*args, **kwargs):
    kwargs.update(cls=DecimalEncoder)
    return json.dumps(*args, **kwargs)


db = SQLAlchemy(engine_options={'json_serializer': dumps})


def as_dict(instance):
    ''' Transform a model instance into a dict '''
    return {
        c.name: getattr(instance, c.name)
        for c in instance.__table__.columns
    }
