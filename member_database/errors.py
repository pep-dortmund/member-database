from flask import render_template
from logging.handlers import SMTPHandler
import logging

from .models import db


def not_found_error(error):
    return render_template('errors/404.html'), 404


def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


def unauthorized_error(error):
    return render_template('errors/401.html'), 401


def setup_email_logger(app):
    if not app.debug and app.config['MAIL_SERVER']:

        if app.config['MAIL_USE_SSL']:
            app.logger.warning('SSL not supported by logging.SMTPHandler')
            return

        credentials = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            credentials = (
                app.config['MAIL_USERNAME'],
                app.config['MAIL_PASSWORD'],
            )

        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_SENDER'],
            toaddrs=app.config['ADMIN_MAIL'],
            subject='PeP Database Failure',
            credentials=credentials,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
