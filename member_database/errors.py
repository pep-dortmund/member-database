from flask import render_template

from .models import db


def not_found_error(error):
    return render_template('errors/404.html'), 404


def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


def unauthorized_error(error):
    return render_template('errors/401.html'), 401
