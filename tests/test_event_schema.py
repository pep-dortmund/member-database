from jsonschema import validate, ValidationError
from pytest import raises
import wtforms


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


def test_create_wtform():
    from database.json_forms import create_wtf_form
    schema = [
        {
            'type': 'number',
            'label': 'Semester',
            'id': 'semester',
            'required': True,
        },
        {
            'type': 'text',
            'label': 'title',
            'id': 'title',
            'required': True,
        },
        {
            'type': 'select',
            'label': 'Abschluss',
            'id': 'degree',
            'options': [
                {'value': 'bachelor', 'label': 'Bachelor'},
                {'value': 'master', 'label': 'Master'},
                {'value': 'phd', 'label': 'Promotion'},
            ]
        }
    ]

    Form = create_wtf_form(schema, baseclasses=(wtforms.Form, ))
    form = Form()

    assert isinstance(form.semester, wtforms.FloatField)
    assert isinstance(form.title, wtforms.StringField)
    assert isinstance(form.degree, wtforms.SelectField)
    assert form.degree.choices == [
        ('bachelor', 'Bachelor'), ('master', 'Master'), ('phd', 'Promotion')
    ]

