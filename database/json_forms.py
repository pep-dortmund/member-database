from jsonschema import validate, ValidationError

# json schema definitions for input fields
TEXT_FIELD = {
    'type': 'object',
    'properties': {
        'type': {'type': 'string', 'pattern': 'text'},
        'id': {'type': 'string'},
        'label': {'type': 'string'},
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
        'default': {'type': 'number'},
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
    'items': {'anyOf': [TEXT_FIELD, NUMBER_FIELD, CHECKBOX, SELECT]},
}


def validate_form(form):
    validate(form, FORM)
