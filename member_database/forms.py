from datetime import date

from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import (
    StringField,
    SubmitField,
    ValidationError,
    RadioField,
    BooleanField,
    IntegerField,
)
from wtforms.fields import EmailField, DateField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    Optional,
    Regexp,
    InputRequired,
    StopValidation,
)

from .models import Person, MembershipType, SepaMandate


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


def iban_validator(form, field):
    if field.data == "":
        return
    try:
        SepaMandate.validate_iban(None, None, field.data.replace(" ", ""))
    except ValueError:
        raise ValidationError("Invalid IBAN")


# https://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
# Custom class so html elements dont get the required mark
class RequiredIfNot:
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, message=None):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if not bool(other_field.data):
            if not field.raw_data or not field.raw_data[0]:
                if self.message is None:
                    message = field.gettext("This field is required.")
                else:
                    message = self.message

                field.errors[:] = []
                raise StopValidation(message)


class RequiredIf:
    # a validator which makes a field required if
    # another field is set and has a truthy value

    def __init__(self, other_field_name, message=None):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            if not field.raw_data or not field.raw_data[0]:
                if self.message is None:
                    message = field.gettext("This field is required.")
                else:
                    message = self.message

                field.errors[:] = []
                raise StopValidation(message)


def beitrag_validator(form, field):
    other_field = form._fields.get("given")
    if bool(other_field.data):
        RequiredIfNot(
            "default",
            message="Muss ausgefüllt werden, falls nicht der vorgeschlagenene Beitrag bezahlt werden soll.",
        )(form, field)


class SepaForm(FlaskForm):
    adress = TextAreaField(_l("Adresse"), validators=[RequiredIf("given")])
    iban = StringField(_l("IBAN"), validators=[RequiredIf("given"), iban_validator])
    bank = StringField(_l("Bankinstitut"), validators=[RequiredIf("given")])

    default = BooleanField(
        _l("Von der Beitragsordnung vorgeschlagenen Beitrag zahlen"),
        validators=[],
        description="Ich möchte den in im Jahr der Abbuchung für mich in der vom Vorstand beschlossenen Beitragsordnung vorgeschlagenen Mitgliedsbeitrag zahlen.",
    )
    value = StringField(
        _l("Förderbeitrag in Euro"),
        validators=[
            Regexp(
                "^(|\d+((,|\.)\d{2})?)$",
                message="Muss der Form '4.20', '42,10' oder '50' entsprechend.",
            ),
            beitrag_validator,
        ],
        description="Einfach leer lassen, wenn der vorgeschlagene Beitrag bezahlt werden soll.",
    )

    # can also be un-given
    given = BooleanField(
        # _l("Mandat erteilen und folgende Bedingungen akzeptieren"),
        (
            "Ich ermächtige PeP et al. eV. (SEPA Gläubiger-ID: XXX), Zahlungen von meinem Konto mittels Lastschrift einzuziehen. "
            "Zugleich weise ich mein Kreditinstitut an, die von PeP et al. eV. auf mein Konto "
            "gezogenen Lastschriften einzulösen. "
            "Der Mitglieds oder Förderbeitrag wird dabei einmal im Jahr von PeP et al. eV. eingezogen"
            "Hinweis: Ich kann innerhalb von acht Wochen, beginnend mit dem Belastungsdatum, "
            "die Erstattung des belasteten Betrages verlangen."
            "Es gelten dabei die mit meinem Kreditinstitut vereinbarten Bedingungen."
        ),
        validators=[],
    )
    submit = SubmitField(_l("Speichern"))
