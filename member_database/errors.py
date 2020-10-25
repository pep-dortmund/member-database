from flask import render_template
from flask_login import current_user

from .authentication import LoginForm
from .models import db


def not_found_error(error):
    return render_template('errors/404.html'), 404


def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


def unauthorized_error(error):
    '''Render login form on authorization error'''
    if current_user.is_authenticated:
        return render_template('errors/401.html'), 401

    form = LoginForm()
    # do not overwrite next if it is already set
    next_link = request.args.get('next', request.full_path)
    return render_template(
        'simple_form.html', title='Login',
        form=form, action=url_for('main.login_page', next=next_link),
    ), 401
