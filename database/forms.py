from flask_wtf import FlaskForm
from flask_babel import _
from wtforms import StringField, SubmitField, DateField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Optional


class PersonEditForm(FlaskForm):
    name = StringField(_('Name'), validators=[DataRequired()])
    email = EmailField(_('E-Mail-Adresse'), validators=[DataRequired(), Email()])
    date_of_birth = DateField(_('Geburtstag'),
                              validators=[Optional()],
                              format=_('%d.%m.%Y'))
    joining_date = DateField(_('Mitglied seit'), render_kw={'readonly': True})
    membership_pending = BooleanField(_('Mitgliedschaft beantragt'))
    member = BooleanField(_('Mitgliedschaft bestätigt'),
                          render_kw={'readonly': True})
    submit = SubmitField(_('Speichern'))
