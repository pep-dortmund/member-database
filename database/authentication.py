from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from .models import User


login = LoginManager()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class LoginForm(FlaskForm):
    user_or_email = StringField('Username/Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')
