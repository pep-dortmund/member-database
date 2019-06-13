from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect, url_for, request, flash, abort
import base64

from .models import User


login = LoginManager()


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
    if request.headers.get('Authorization') is not None:
        abort(401)

    flash("You have to be logged in to access this page.")
    return redirect(url_for('login', next=request.endpoint))


class LoginForm(FlaskForm):
    user_or_email = StringField('Username/Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')
