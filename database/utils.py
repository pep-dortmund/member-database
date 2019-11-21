from sqlalchemy.sql.expression import ClauseElement
from flask import url_for, current_app
from .models import db


def get_or_create(model, defaults=None, **kwargs):
    '''
    Check if there is already a row in the database which matches
    the kwargs, create if not.

    See https://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create

    Parameters
    ----------
    model: Model
        the db tabel to qery
    defaults: dict
        If a new instance will be created, use this dict for as default values
    **kwargs:
        columns to filter by, e.g. `email='user@example.org'`
    '''
    q = model.query.filter_by(**kwargs)

    # make sure the query is unambiguous
    if q.count() > 1:
        raise ValueError('Query matches multiple entries')

    instance = q.first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        db.session.add(instance)
        return instance, True


def ext_url_for(*args, **kwargs):
    return url_for(
        *args, **kwargs,
        _external=True,
        _scheme='https' if current_app.config['USE_HTTPS'] else 'http',
    )
