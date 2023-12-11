import decimal
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


class DecimalEncoder(json.JSONEncoder):
    """Need to encode decimal objects from the html5.decimalinput fields
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


# necessary for named indexes to work in migrations
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
db = SQLAlchemy(
    engine_options={"json_serializer": dumps},
    metadata=MetaData(naming_convention=naming_convention),
)


def as_dict(instance):
    """Transform a model instance into a dict"""
    return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
