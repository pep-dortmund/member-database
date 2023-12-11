import logging
from sqlite3 import Connection as SQLite3Connection

from flask import Flask, request
from flask_babel import Babel
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .admin_views import create_admin_views
from .authentication import auth, init_authentication_database, login
from .config import Config
from .errors import internal_error, not_found_error, unauthorized_error
from .events import events, init_event_database
from .json import JSONEncoderISO8601
from .log import setup_logging
from .mail import mail
from .main import init_main_database, main
from .models import db


@event.listens_for(Engine, "connect")
def pragma_on_connect(dbapi_con, con_record):
    """
    Make sure sqlite uses foreing key constraints
    https://stackoverflow.com/a/15542046/3838691
    """
    if isinstance(dbapi_con, SQLite3Connection):
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    mail.init_app(app)
    login.init_app(app)
    Migrate(app, db, render_as_batch=True)
    Bootstrap4(app)
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(app.config["LANGUAGES"])

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(events, url_prefix="/events")

    app.json_provider_class = JSONEncoderISO8601

    app.register_error_handler(401, unauthorized_error)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(500, internal_error)

    setup_logging(app)

    admin = create_admin_views()
    admin.init_app(app)

    app.logger.setLevel(logging.INFO)
    app.logger.info("App created")

    app.logger.info("Initializing app dbs")
    with app.app_context():
        init_authentication_database()
        init_main_database()
        init_event_database()
        app.logger.info("app db initialized")

    return app
