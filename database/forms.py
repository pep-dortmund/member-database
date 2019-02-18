from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Optional


class PersonEditForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('E-Mail-Adresse', validators=[DataRequired(), Email()])
    date_of_birth = DateField('Geburtstag', validators=[Optional()])
    joining_date = DateField('Mitglied seit', render_kw={'readonly': True})
    submit = SubmitField('Speichern')
