from flask_wtf import FlaskForm
import wtforms
from wtforms.fields import (
    TextAreaField,
    EmailField,
    IntegerField,
    DecimalField,
    HiddenField,
)
from wtforms.validators import DataRequired, NumberRange, Regexp
from markupsafe import Markup

from ..widgets import LatexInput


def create_wtf_field(name, schema, required=True):
    validators = []

    kwargs = {
        "default": schema.get("default"),
        "validators": validators,
        "label": Markup(schema.get("label", name.title())),
    }

    message = schema.get("error_hint")

    if required:
        validators.append(DataRequired(message=message))

    if schema.get("pattern"):
        validators.append(Regexp(schema["pattern"], message=message))

    if schema["type"] == "string":
        fmt = schema.get("format")

        if fmt == "latex":
            kwargs["widget"] = LatexInput()

        elif fmt == "email":
            return EmailField(**kwargs)

        elif fmt == "multiline":
            return TextAreaField(**kwargs)

        elif fmt not in {"radio", "select", None}:
            raise ValueError(f"Unknown format {fmt}")

        if "enum" in schema:
            if fmt == "radio":
                return wtforms.RadioField(
                    **kwargs,
                    choices=[(o, o) for o in schema["enum"]],
                )
            return wtforms.SelectField(
                **kwargs, choices=[(o, o) for o in schema["enum"]]
            )

        return wtforms.StringField(**kwargs)

    if schema.get("minimum") or schema.get("maximum"):
        validators.append(
            NumberRange(schema.get("minimum"), schema.get("maximum"), message=message)
        )

    if schema["type"] == "integer":
        return IntegerField(**kwargs)

    if schema["type"] == "number":
        return DecimalField(**kwargs)

    if schema["type"] == "boolean":
        # forces checkbox to be clicked
        if schema.get("const") is not None:
            validators.append(DataRequired())
        return wtforms.BooleanField(**kwargs)

    # this can be used to show only a message
    if schema["type"] == "null":
        return HiddenField(**kwargs)

    # subform
    if schema["type"] == "object":
        # baseclass needs to be wtforms.Form so the subforms do not include
        # the csrf token
        form = create_wtf_form(schema, baseclasses=(wtforms.Form,), submit=False)
        return wtforms.FormField(form, **kwargs)

    raise ValueError(f'Unknown type {schema["type"]}')


def create_wtf_form(
    schema, baseclasses=(FlaskForm,), additional_fields=None, submit=True
):
    """
    Create a WTForms class from a json schema
    """
    attrs = {}
    required = schema.get("required", [])

    if additional_fields is not None:
        for name, field in additional_fields.items():
            attrs[name] = field

    if "properties" in schema:
        for name, field_schema in schema["properties"].items():
            attrs[name] = create_wtf_field(
                name,
                field_schema,
                required=name in required,
            )

    if submit:
        attrs["submit"] = wtforms.SubmitField("Anmelden")

    return type("JSONForm", baseclasses, attrs)
