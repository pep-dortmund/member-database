from jsonschema import validate, ValidationError
from pytest import raises


def test_textfield():
    from database.json_forms import TEXT_FIELD

    validate({'type': 'text', 'label': 'Name', 'id': 'name'}, TEXT_FIELD)

    with raises(ValidationError):
        validate({'type': 'foo', 'label': 'name', 'id': 'name'}, TEXT_FIELD)


def test_form():
    from database.json_forms import validate_form

    validate_form([
        {'type': 'text', 'label': 'Name', 'id': 'name'},
        {'type': 'number', 'label': 'Alter', 'id': 'age'},
    ])

    validate_form([
        {'type': 'number', 'label': 'Alter', 'id': 'age'},
    ])

    validate_form([
        {
            'type': 'select',
            'label': 'Abschluss',
            'id': 'degree',
            'options': [
                {'value': 'bachelor', 'label': 'Bachelor'},
                {'value': 'master', 'label': 'Master'},
                {'value': 'phd', 'label': 'Promotion'},
            ]
        },
    ])
