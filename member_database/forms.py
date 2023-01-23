from datetime import date

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, ValidationError, RadioField
from wtforms.fields import EmailField, DateField
from wtforms.validators import DataRequired, Email, Optional

from .models import Person, MembershipType


def known_email(form, field):
    p = Person.query.filter_by(email=field.data).one_or_none()
    if p is None:
        raise ValidationError("Unbekannte Email-Adresse")


def not_in_future(form, field):
    if field.data > date.today():
        raise ValidationError("Datum darf nicht in der Zukunft liegen")


class PersonEditForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired()])
    email = EmailField(
        _l("E-Mail-Adresse"),
        validators=[DataRequired(), Email()],
        render_kw={"readonly": True},
    )
    tu_status = RadioField(
        _l("Aktuelles Verhältnis zur TU Dortmund"), validators=[Optional()]
    )
    date_of_birth = DateField(_l("Geburtstag"), validators=[Optional(), not_in_future])
    joining_date = DateField(
        _l("Mitglied seit"), render_kw={"readonly": True}, validators=[Optional()]
    )
    membership_status = StringField(
        _l("Mitgliedschaftsstatus"), render_kw={"readonly": True}
    )
    membership_type = RadioField(
        _l("Art der Mitgliedschaft"),
        choices=[
            (MembershipType.ORDENTLICH, "Ordentliches Mitglied"),
            (MembershipType.AUSSERORDENTLICH, "Außerordentliches Mitglied"),
        ],
        validators=[Optional()],
    )
    submit = SubmitField(_l("Speichern"))


class MembershipForm(FlaskForm):
    name = StringField(_l("Name"), validators=[DataRequired()])
    email = EmailField(_l("E-Mail-Adresse"), validators=[DataRequired(), Email()])
    membership_type = RadioField(
        _l("Art der Mitgliedschaft"),
        choices=[
            (MembershipType.ORDENTLICH, "Ordentliches Mitglied"),
            (MembershipType.AUSSERORDENTLICH, "Außerordentliches Mitglied"),
        ],
        default=MembershipType.ORDENTLICH,
        description=(
            "Alle Angehörigen oder ehemaligen Angehörigen der Fakultät Physik der TU Dortmund können und sollten ordentliche Mitglieder werden."
            " Für alle anderen besteht die Möglichkeit einer außerordentlichen Mitgliedschaft."
        ),
    )
    submit = SubmitField(_l("Mitgliedsantrag abschicken"))


class RequestLinkForm(FlaskForm):
    email = EmailField(
        _l("E-Mail-Adresse"), validators=[DataRequired(), Email(), known_email]
    )
    submit = SubmitField()
