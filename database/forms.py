from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from flask_babel import _
from wtforms import StringField, SubmitField, DateField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Optional


class PersonEditForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    email = EmailField(_l('E-Mail-Adresse'), validators=[DataRequired(), Email()])
    date_of_birth = DateField(_l('Geburtstag'),
                              validators=[Optional()],
                              format='%d.%m.%Y')
    joining_date = DateField(_l('Mitglied seit'), render_kw={'readonly': True})
    membership_pending = BooleanField(_l('Mitgliedschaft beantragt'))
    member = BooleanField(_l('Mitgliedschaft bestätigt'),
                          render_kw={'readonly': True})
    submit = SubmitField(_l('Speichern'))
