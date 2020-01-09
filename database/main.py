from flask import (
    jsonify, request, url_for, render_template, redirect,
    flash, abort, Blueprint, current_app
)
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData

from sqlalchemy.exc import IntegrityError

from .models import db, Person, User, as_dict
from .utils import get_or_create, ext_url_for
from .authentication import LoginForm, access_required
from .forms import PersonEditForm
from .mail import send_email


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('base.html')


@main.route('/persons', methods=['GET'])
@access_required('get_persons')
def get_persons():
    persons = [as_dict(person) for person in Person.query.all()]
    return jsonify(status='success', persons=persons)


@main.route('/persons', methods=['POST'])
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


@main.route('/members', methods=['GET'])
@access_required('get_members')
def get_members():
    '''Return a json list with all current members'''
    members = Person.query.filter_by(member=True).all()
    members = [as_dict(member) for member in members]
    return jsonify(status='success', members=members)


@main.route('/members', methods=['POST'])
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

    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(p.email, salt='edit-key')

    send_email(
        subject=_('Willkommen bei PeP et al. e.V.'),
        sender=current_app.config['MAIL_SENDER'],
        recipients=[p.email],
        body=render_template(
            'mail/welcome.txt',
            new_member=p,
            url=ext_url_for('edit', token=token),
        )
    )

    return jsonify(status='success')


@main.route('/request_edit', methods=['POST'])
def send_edit_token():
    '''
    Request a link to edit personal data
    '''
    email = request.get_json()['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(email, salt='edit-key')

    send_email(
        subject=_('PeP et al. e.V. Mitgliedsdatenänderung'),
        sender=current_app.config['MAIL_SENDER'],
        recipients=[email],
        body=render_template(
            'mail/edit_mail.txt',
            edit_link=ext_url_for('edit', token=token),
        )
    )

    return jsonify(status='success', message='Edit mail sent')


@main.route('/request_gdpr_data', methods=['POST'])
def send_request_data_token():
    '''
    Request a link to view personal data
    '''
    email = request.form['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(email, salt='request_gdpr_data-key')

    send_email(
        subject='PeP et al. e.V. - Einsicht in gespeicherte Daten',
        sender=current_app.config['MAIL_SENDER'],
        recipients=[email],
        body=render_template(
            'mail/request_data_mail.txt',
            data_link=ext_url_for('view_data', token=token),
        )
    )
    return jsonify(status='success', message='GDPR data request mail sent')


@main.route('/edit/<token>', methods=['GET', 'POST'])
def edit(token):
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(
            token,
            salt='edit-key',
            max_age=current_app.config['TOKEN_MAX_AGE'],
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
            sender=current_app.config['MAIL_SENDER'],
            recipients=[current_app.config['APPROVE_MAIL']],
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
        return redirect(url_for('main.edit', token=token))


@main.route('/view_data/<token>')
def view_data(token):
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
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


@main.route('/applications')
@access_required('view_applications')
def applications():
    applications = Person.query.filter_by(membership_pending=True).all()
    return render_template('applications.html', applications=applications)


@main.route('/login', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_or_email = form.user_or_email.data
        user = User.query.filter(
            (User.username == user_or_email) | (Person.email == user_or_email)
        ).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid user or password', 'danger')
            return redirect(url_for('main.login_page', next=request.args.get('next')))
        login_user(user)
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('login.html', title='Login', form=form)


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))
