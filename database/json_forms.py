from jsonschema import validate
from flask_wtf import FlaskForm
import wtforms
from wtforms import validators

# json schema definitions for input fields
TEXT_FIELD = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'text'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
        'required': {'type': 'boolean'},
    },
    'required': ['type', 'id', 'label'],
}

NUMBER_FIELD = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'number'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
        'min': {'type': 'number'},
        'max': {'type': 'number'},
        'required': {'type': 'boolean'},
    },
    'required': ['type', 'id', 'label'],
}

INTEGER_FIELD = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'integer'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
        'min': {'type': 'integer'},
        'max': {'type': 'integer'},
        'required': {'type': 'boolean'},
    },
    'required': ['type', 'id', 'label'],
}


CHECKBOX = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'checkbox'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
        'default': {'type': 'boolean'},
    },
    'required': ['type', 'id', 'label'],
}

SELECT_OPTION = {
    'type': 'object',
    'properties': {
        'value': {'type': 'string'},
        'label': {'type': 'string'},
    },
    'required': ['value', 'label'],
}

SELECT = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'select'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
        'options': {'type': 'array', 'items': SELECT_OPTION},
    },
    'required': ['type', 'id', 'label'],
}


FORM = {
    'type': 'array',
    'items': {'anyOf': [TEXT_FIELD, INTEGER_FIELD, NUMBER_FIELD, CHECKBOX, SELECT]},
}


def validate_form(form):
    validate(form, FORM)


def create_wtf_field(schema):
    kwargs = {'validators': []}
    if schema.get('required', False):
        kwargs['validators'].append(validators.DataRequired())

    if schema['type'] == 'text':
        return wtforms.StringField(**kwargs)

    if schema['type'] == 'select':
        kwargs['choices'] = [(o['value'], o['label']) for o in schema['options']]
        return wtforms.SelectField(**kwargs)

    # number stuff:
    if schema.get('min') or schema.get('max'):
        kwargs['validators'].append(
            validators.NumberRange(schema.get('min'), schema.get('max'))
        )

    if schema['type'] == 'integer':
        return wtforms.IntegerField(**kwargs)
    if schema['type'] == 'number':
        return wtforms.FloatField(**kwargs)

    raise ValueError(f'Unknown type {schema["type"]}')


def create_wtf_form(schema, baseclasses=(FlaskForm, )):
    validate_form(schema)

    attrs = {}
    for field in schema:
        attrs[field['id']] = create_wtf_field(field)

    return type('JSONForm', baseclasses, attrs)
