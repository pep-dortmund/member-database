import wtforms


def has_validator(field, validator_cls):
    return any(isinstance(v, validator_cls) for v in field.validators)


def test_empty():
    """Test empty schema works"""
    from member_database.events.json_forms import create_wtf_form

    schema = {}

    Form = create_wtf_form(schema, baseclasses=(wtforms.Form,))
    form = Form()
    assert isinstance(form.submit, wtforms.SubmitField)


def test_basic_elements():
    from member_database.events.json_forms import create_wtf_form

    schema = dict(
        type="object",
        properties={
            "name": {"type": "string", "label": "Name"},
            "email": {"type": "string", "format": "email"},
            "semester": {"type": "integer", "label": "Semester"},
            "degree": {
                "type": "string",
                "label": "Abschluss",
                "enum": ["Bachelor", "Master", "Promotion"],
            },
            "vegan": {"type": "boolean"},
        },
        required=["name", "semester", "degree"],
    )

    Form = create_wtf_form(schema, baseclasses=(wtforms.Form,))
    form = Form()

    assert isinstance(form.name, wtforms.StringField)
    assert has_validator(form.name, wtforms.validators.DataRequired)
    assert isinstance(form.semester, wtforms.IntegerField)
    assert isinstance(form.degree, wtforms.SelectField)
    assert isinstance(form.email, wtforms.EmailField)

    assert form.degree.choices == [
        ("Bachelor", "Bachelor"),
        ("Master", "Master"),
        ("Promotion", "Promotion"),
    ]

    assert isinstance(form.vegan, wtforms.BooleanField)


def test_subform():
    from member_database.events.json_forms import create_wtf_form

    subform = dict(
        type="object",
        properties=dict(
            cpp=dict(type="boolean"),
            c=dict(type="boolean"),
            python=dict(type="boolean"),
            other=dict(type="string"),
        ),
    )

    schema = dict(
        type="object",
        properties=dict(
            languages=subform,
            name=dict(type="string"),
        ),
    )

    Form = create_wtf_form(schema, baseclasses=(wtforms.Form,))
    form = Form()

    assert isinstance(form.languages, wtforms.FormField)
    assert isinstance(form.languages.cpp, wtforms.BooleanField)
    assert isinstance(form.languages.c, wtforms.BooleanField)
    assert isinstance(form.languages.python, wtforms.BooleanField)
    assert isinstance(form.languages.other, wtforms.StringField)
    assert isinstance(form.name, wtforms.StringField)
