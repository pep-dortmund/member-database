from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileRequired

from wtforms.fields.html5 import EmailField
from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired


class SendMailForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])

    subject = StringField('Subject', validators=[DataRequired()])
    body = TextAreaField('Inhalt', validators=[DataRequired()])

    attachments = MultipleFileField('Anhänge')
    submit = SubmitField('Email senden')
