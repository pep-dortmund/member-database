from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    user_or_email = StringField('Username/Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Login')


class SendPasswordResetForm(FlaskForm):
    user_or_email = StringField('Username/Email', validators=[DataRequired()])
    submit = SubmitField('Send password reset email')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField(
        'New password',
        validators=[
            DataRequired(),
            EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset password')
