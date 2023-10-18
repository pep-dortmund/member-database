from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, TextAreaField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired

# from flask_wtf.file import FileField, FileRequired


class SendMailForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])

    subject = StringField("Subject", validators=[DataRequired()])
    body = TextAreaField("Inhalt", validators=[DataRequired()])

    attachments = MultipleFileField("Anhänge")
    submit = SubmitField("Email senden")
