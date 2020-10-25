from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Email, Optional


class PersonEditForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('E-Mail-Adresse'), validators=[DataRequired(), Email()])
    date_of_birth = DateField(_l('Geburtstag'), validators=[Optional()])
    joining_date = DateField(_l('Mitglied seit'), render_kw={'readonly': True})
    membership_status = StringField(_l('Mitgliedschaftsstatus'), render_kw={'readonly': True})
    submit = SubmitField(_l('Speichern'))


class MembershipForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('E-Mail-Adresse'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Mitgliedsantrag abschicken'))
