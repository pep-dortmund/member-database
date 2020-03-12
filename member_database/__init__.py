from flask import Flask, request
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_babel import Babel


from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

import logging

from .config import Config
from .models import db
from .authentication import login
from .mail import mail
from .errors import not_found_error, internal_error, unauthorized_error
from .log import setup_logging
from .events import events
from .json import JSONEncoderISO8601
from .main import main
from .admin_views import create_admin_views


@event.listens_for(Engine, 'connect')
def pragma_on_connect(dbapi_con, con_record):
    '''
    Make sure sqlite uses foreing key constraints
    https://stackoverflow.com/a/15542046/3838691
    '''
    if isinstance(dbapi_con, SQLite3Connection):
        cursor = dbapi_con.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.close()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    mail.init_app(app)
    login.init_app(app)
    Migrate(app, db)
    Bootstrap(app)
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    app.register_blueprint(main)
    app.register_blueprint(events, url_prefix='/events')

    app.json_encoder = JSONEncoderISO8601

    app.register_error_handler(401, unauthorized_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    setup_logging(app)

    admin = create_admin_views()
    admin.init_app(app)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App created')

    return app
