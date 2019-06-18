from flask import Flask, jsonify, request, url_for, render_template, redirect, flash
from flask_migrate import Migrate
from flask_login import current_user, login_user, logout_user, login_required
from flask_bootstrap import Bootstrap
from flask import abort
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired
from functools import partial
import logging


from sqlalchemy.exc import IntegrityError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from .config import Config
from .models import db, Person, User, as_dict
from .utils import get_or_create
from .authentication import login, LoginForm
from .mail import mail, send_email
from .errors import not_found_error, internal_error, email_logger


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

app.register_error_handler(404, not_found_error)
app.register_error_handler(500, internal_error)
email_logger(app)

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])


ext_url_for = partial(
    url_for,
    _external=True,
    _scheme='https' if app.config['USE_HTTPS'] else 'http',
)


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/persons', methods=['GET'])
@login_required
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
def get_members():
    '''Return a json list with all current members'''
    members = Person.query.filter_by(member=True).all()
    persons = [as_dict(member) for member in members]
    return jsonify(status='success', persons=persons)


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
        subject='Willkommen bei PeP et al. e.V.',
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
    email = request.form['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    token = ts.dumps(email, salt='edit-key')

    send_email(
        subject='PeP et al. e.V. Mitgliedsdatenänderung',
        sender=app.config['MAIL_SENDER'],
        recipients=[email],
        body=render_template(
            'mail/edit_mail.txt',
            edit_link=ext_url_for('edit', token=token),
        )
    )

    return jsonify(status='success', message='Edit mail sent.')


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
            edit_link=ext_url_for('view_data', token=token),
        )
    )
    return jsonify(status='success', message='Edit mail sent.')



@app.route('/edit/<token>')
def edit(token):
    try:
        email = ts.loads(token, salt='edit-key')
    except SignatureExpired:
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
        flash('Willkommen bei PeP et al. e.V.!')

        p.email_valid = True
        db.session.add(p)
        db.session.commit()

    pass


@app.route('/view_data/<token>')
def view_data(token):
    try:
        email = ts.loads(token, salt='request_gdpr_data-key')
    except SignatureExpired:
        abort(404)

    p = Person.query.filter_by(email=email)
    personal_data = as_dict(p)

    if p is None:
        abort(404)

    return jsonify(status='success', personal_data=personal_data)

@app.route('/edit/<token>', methods=['POST'])
def save_edit(token):
    pass


@app.route('/applications')
@login_required
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
        return redirect(request.args.get('next', url_for('index')))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/test_error')
def throw_test_error():
    app.logger.error('test error')
