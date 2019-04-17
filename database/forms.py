from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Optional


class WTFormsTranslator():
    def gettext(self, string):
        return _l(string)


class TranslatedForm(FlaskForm):
    def _get_translations(self):
        return WTFormsTranslator()


class PersonEditForm(TranslatedForm):
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
