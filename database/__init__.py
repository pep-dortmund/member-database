from flask import (Flask, jsonify, request, url_for, render_template, redirect,
                   flash, abort)
from flask_migrate import Migrate
from flask_login import current_user, login_user, logout_user
from flask_bootstrap import Bootstrap
from flask_babel import Babel, _
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData
from functools import partial
import logging


from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from wtforms.fields import StringField
from wtforms.fields.html5 import EmailField

from .config import Config
from .models import db, Person, User, as_dict, Event, EventRegistration
from .json_forms import create_wtf_form
from .utils import get_or_create
from .authentication import login, LoginForm, access_required
from .forms import PersonEditForm
from .mail import mail, send_email
from .errors import not_found_error, internal_error, email_logger, unauthorized_error


@event.listens_for(Engine, 'connect')
def pragma_on_connect(dbapi_con, con_record):
    '''
    Make sure sqlite uses foreing key constraints
    https://stackoverflow.com/a/15542046/3838691
    '''
    if isinstance(dbapi_con, SQLite3Connection):
        cursor = dbapi_con.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.close()


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)
login.init_app(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
babel = Babel(app)

app.register_error_handler(401, unauthorized_error)
app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)
email_logger(app)

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])


ext_url_for = partial(
    url_for,
    _external=True,
    _scheme='https' if app.config['USE_HTTPS'] else 'http',
)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/persons', methods=['GET'])
@access_required('get_persons')
def get_persons():
    persons = [as_dict(person) for person in Person.query.all()]
    return jsonify(status='success', persons=persons)


@app.route('/persons', methods=['POST'])
def add_person():
    '''
    Add a new person via a http post request using a json payload
    that has name and email.
    '''
    data = request.get_json()

    try:
        p = Person(name=data['name'], email=data['email'])
        db.session.add(p)
        db.session.commit()
    except KeyError as e:
        return jsonify(
            status='error',
            message='Missing required parameter {}'.format(e.args[0])
        ), 422
    except IntegrityError:
        return jsonify(
            status='error',
            message='Person already exists',
        ), 422

    return jsonify(status='success')


@app.route('/members', methods=['GET'])
@access_required('get_members')
def get_members():
    '''Return a json list with all current members'''
    members = Person.query.filter_by(member=True).all()
    members = [as_dict(member) for member in members]
    return jsonify(status='success', members=members)


@app.route('/members', methods=['POST'])
def add_member():
    '''
    Create a new Person or find an existing one by email
    and set it's member attribute to True.
    Send an email to the board to notify them of a new membership application.
    '''
    data = request.get_json()

    try:
        p, new = get_or_create(
            Person,
            email=data['email'],
            defaults={'name': data['name']}
        )
    except KeyError as e:
        return jsonify(
            status='error',
            message='Missing required parameter {}'.format(e.args[0])
        ), 422

    if p.member:
        return jsonify(status='error', message='Already member'), 422

    p.membership_pending = True
    db.session.add(p)
    db.session.commit()

    token = ts.dumps(p.email, salt='edit-key')

    send_email(
        subject=_('Willkommen bei PeP et al. e.V.'),
        sender=app.config['MAIL_SENDER'],
        recipients=[p.email],
        body=render_template(
            'mail/welcome.txt',
            new_member=p,
            url=ext_url_for('edit', token=token),
        )
    )

    return jsonify(status='success')


@app.route('/request_edit', methods=['POST'])
def send_edit_token():
    '''
    Request a link to edit personal data
    '''
    email = request.get_json()['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    token = ts.dumps(email, salt='edit-key')

    send_email(
        subject=_('PeP et al. e.V. Mitgliedsdatenänderung'),
        sender=app.config['MAIL_SENDER'],
        recipients=[email],
        body=render_template(
            'mail/edit_mail.txt',
            edit_link=ext_url_for('edit', token=token),
        )
    )

    return jsonify(status='success', message='Edit mail sent')


@app.route('/request_gdpr_data', methods=['POST'])
def send_request_data_token():
    '''
    Request a link to view personal data
    '''
    email = request.form['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    token = ts.dumps(email, salt='request_gdpr_data-key')

    send_email(
        subject='PeP et al. e.V. - Einsicht in gespeicherte Daten',
        sender=app.config['MAIL_SENDER'],
        recipients=[email],
        body=render_template(
            'mail/request_data_mail.txt',
            data_link=ext_url_for('view_data', token=token),
        )
    )
    return jsonify(status='success', message='GDPR data request mail sent')


@app.route('/edit/<token>', methods=['GET', 'POST'])
def edit(token):
    try:
        email = ts.loads(
            token,
            salt='edit-key',
            max_age=app.config['TOKEN_MAX_AGE'],
        )
    except SignatureExpired:
        flash(_('Ihre Sitzung ist abgelaufen'))
    except BadData:
        abort(404)

    p = Person.query.filter_by(email=email).first()
    if p is None:
        abort(404)

    # guessing the member just signed up if the email is not validated yet
    if not p.email_valid:
        send_email(
            subject='Neuer Mitgliedsantrag',
            sender=app.config['MAIL_SENDER'],
            recipients=[app.config['APPROVE_MAIL']],
            body=render_template(
                'mail/approve_member.txt',
                new_member=p,
                url=ext_url_for('applications'),
            )
        )
        flash(_('Willkommen bei PeP et al. e.V.!'))

        p.email_valid = True
        db.session.add(p)
        db.session.commit()

    form = PersonEditForm(
        name=p.name,
        email=p.email,
        date_of_birth=p.date_of_birth,
        joining_date=p.joining_date,
        membership_pending=p.membership_pending,
        member=p.member,
    )

    if form.validate_on_submit():
        p.name = form.name.data
        if p.email != form.email.data:
            p.email_valid = False
            p.email = form.email.data
        p.date_of_birth = form.date_of_birth.data
        p.membership_pending = form.membership_pending.data
        db.session.commit()
        flash(_('Ihre Daten wurden erfolgreich aktualisiert.'))
        return redirect(url_for('edit', token=token))


@app.route('/view_data/<token>')
def view_data(token):
    try:
        email = ts.loads(token, salt='request_gdpr_data-key')
    except SignatureExpired:
        flash(_('Ihre Sitzung ist abgelaufen'))
    except BadData:
        abort(404)

    p = Person.query.filter_by(email=email)

    if p is None:
        abort(404)

    personal_data = as_dict(p)

    return jsonify(status='success', personal_data=personal_data)


@app.route('/applications')
@access_required('view_applications')
def applications():
    applications = Person.query.filter_by(membership_pending=True).all()
    return render_template('applications.html', applications=applications)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_or_email = form.user_or_email.data
        user = User.query.filter(
            (User.username == user_or_email) | (Person.email == user_or_email)
        ).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user or password', 'danger')
            return redirect(url_for('login', next=request.args.get('next')))
        login_user(user)
        return redirect(url_for(request.args.get('next', 'index')))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/test_error')
def throw_test_error():
    app.logger.error('test error')


@app.route('/events/<int:event_id>/registration', methods=['GET', 'POST'])
def registration(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        abort(404)

    if not event.registration_open:
        flash(f'Eine Anmeldung für "{event.name}" is derzeit nicht möglich', 'danger')
        return redirect(url_for('index'))

    form = create_wtf_form(
        event.registration_schema,
        additional_fields={'name': StringField(), 'email': EmailField()}
    )

    if form.validate_on_submit():
        person, _ = get_or_create(Person, email=form.email.data, defaults={'name': form.name.data})
        data = form.data
        for key in ('name', 'email', 'csrf_token'):
            data.pop(key)

        registration, new = get_or_create(
            EventRegistration,
            person_id=person.id,
            event_id=event.id,
            defaults={'data': data, 'status': 'pending'},
        )

        if not new:
            if registration.status == 'pending':
                flash(
                    'Du hast bereits eine Anmeldung für diese Veranstaltung abgeschickt aber die Anmeldung nocht nicht bestätigt.'
                    ' Bitte klicke auf den Link in der Bestätigungsmail',
                    category='danger'
                )
            elif registration.status == 'registered':
                flash('Du bist bereits angemeldet. Falls du deine Daten ändern möchtest, klicke auf den Link in der Bestätigungsmail', category='danger')
        else:
            flash('Um deine Registrierung abzuschließen, klicke auf den Bestätigungslink in der Email, die wir dir geschickt haben! Erst dann bist du angemeldet.', category='success')

        db.session.commit()
        return redirect(url_for('index'))

    return render_template(
        'event_registration.html',
        form=form, event=event,
        url=f'/event/{event_id}/registration',
    )


@app.route('/events/<int:event_id>')
def get_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return jsonify(status='No such event'), 404

    return jsonify(
        status='success',
        event=as_dict(event),
    )
