from jsonschema import validate, ValidationError
from pytest import raises
import wtforms
from wtforms.fields import html5


def has_validator(field, validator_cls):
    return any(isinstance(v, validator_cls) for v in field.validators)


def test_basic_elements():
    from database.json_forms import create_wtf_form
    schema = dict(
        type='object',
        properties={
            'name': {'type': 'string', 'label': 'Name'},
            'semester': {'type': 'integer', 'label': 'Semester'} ,
            'degree': {'type': 'string', 'label': 'Abschluss', 'enum': ['Bachelor', 'Master', 'Promotion']},
            'vegan': {'type': 'boolean'}
        },
        required=['name', 'semester', 'degree'],
    )

    form = create_wtf_form(schema, baseclasses=(wtforms.Form, ))

    assert isinstance(form.name, wtforms.StringField)
    assert has_validator(form.name, wtforms.validators.DataRequired)
    assert isinstance(form.semester, html5.IntegerField)
    assert isinstance(form.degree, wtforms.SelectField)
    assert form.degree.choices == [
        ('bachelor', 'Bachelor'), ('master', 'Master'), ('promotion', 'Promotion')
    ]

    assert isinstance(form.vegan , wtforms.BooleanField)
