from flask_login import LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect, url_for, request, flash, abort, jsonify
import base64
from functools import wraps

from .models import User


login = LoginManager()


def access_required(name):
    '''
    Check if current_user has a role with access_level named `name`.
    Abort request with 401, if that's not the case.

    Usage:
        Decorate view function (`app.route(...)`) with this decorator and
        specify a name of an access_level. The name will be compared to
        all access_levels of all rules of the current_user.
    '''
    def access_decorator(func):
        @wraps(func)
        @login_required  # first of all a use needs to be logged in
        def decorated_function(*args, **kwargs):
            if not current_user.has_access(name):
                abort(401)

            return func(*args, **kwargs)
        return decorated_function
    return access_decorator


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.request_loader
def load_user_from_request(request):

    basic_auth = request.headers.get('Authorization')

    if basic_auth:
        basic_auth = basic_auth.replace('Basic ', '', 1)
        try:
            basic_auth = base64.b64decode(basic_auth)
            user, password = basic_auth.decode().split(':')
        except (TypeError, ValueError):
            # a failed attempt should take as long
            # as a successfull one, thus we do not exit early
            # but perform the database request anyway
            user = None
            password = ''

        user = User.query.filter_by(username=user).first()

        if user and user.check_password(password) is True:
            return user

    return None


@login.unauthorized_handler
def handle_needs_login():
    if 'application/json' in request.headers.get('Accept'):
        return jsonify(status='access_denied'), 401

    if request.headers.get('Authorization') is not None:
        abort(401)

    flash("You have to be logged in to access this page.")
    return redirect(url_for('login_page', next=request.full_path))


class LoginForm(FlaskForm):
    user_or_email = StringField('Username/Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')
