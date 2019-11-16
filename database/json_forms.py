from jsonschema import validate
from flask_wtf import FlaskForm
import wtforms
from wtforms.fields import html5
from wtforms.validators import DataRequired, NumberRange


def sanitize(option):
    return (
        option
        .lower()
        .replace(' ', '_')
    )


def create_wtf_field(schema, required=True):
    validators = []

    kwargs = {
        'validators': validators,
        'label': schema.get('label', ''),
    }

    if required:
        validators.append(DataRequired())

    if schema['type'] == 'string':
        if 'enum' in schema:
            return wtforms.SelectField(
                **kwargs,
                choices=[(sanitize(o), o) for o in schema['enum']]
            )
        return wtforms.StringField(**kwargs)

    if schema.get('minimum') or schema.get('maximum'):
        validators.append(
            NumberRange(schema.get('minimum'), schema.get('maximum'))
        )

    if schema['type'] == 'integer':
        return html5.IntegerField(**kwargs)

    if schema['type'] == 'number':
        return html5.DecimalField(**kwargs)

    if schema['type'] == 'boolean':
        return wtforms.BooleanField(**kwargs)

    raise ValueError(f'Unknown type {schema["type"]}')


def create_wtf_form(schema, baseclasses=(FlaskForm, ), additional_fields=None, data=None):
    attrs = {}
    required = schema.get('required', [])

    if additional_fields is not None:
        for name, field in additional_fields.items():
            attrs[name] = field

    for name, field_schema in schema['properties'].items():
        attrs[name] = create_wtf_field(
            field_schema,
            required=name in required,
        )

    return type('JSONForm', baseclasses, attrs)(data=data)
