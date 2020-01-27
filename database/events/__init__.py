from flask import (
    Blueprint, render_template, abort, flash, redirect, url_for, jsonify, current_app,
    request,
)
from flask_login import current_user
from wtforms.fields import StringField
from wtforms.validators import DataRequired, Regexp
from wtforms.fields.html5 import EmailField
from itsdangerous import URLSafeSerializer, BadData
from flask_babel import _
from jsonschema import validate, ValidationError
from sqlalchemy import func
from datetime import datetime, timezone

from ..models import db, Person, as_dict
from ..utils import get_or_create, ext_url_for
from ..mail import send_email
from ..authentication import access_required

from .models import Event, EventRegistration, RegistrationStatus
from .json_forms import create_wtf_form


__all__ = [
    'events',
    'Event', 'EventRegistration', 'RegistrationStatus',
]


events = Blueprint('events', __name__, template_folder='templates')


def create_email_field(force_tu_mail=False):
    mail_validators = [DataRequired()]

    if force_tu_mail:
        label = 'Email (@tu-dortmund.de)'
        regex = r'^.*@tu-dortmund.de$'
        render_kw = {'pattern': regex}
        mail_validators.append(Regexp(
            regex,
            message=_('Bitte nutze deine @tu-dortmund.de Email-Adresse'),
        ))
    else:
        label = 'Email'
        render_kw = None

    return EmailField(
        label,
        mail_validators,
        render_kw=render_kw,
    )


@events.before_app_first_request
def init_database():
    for name in ('confirmed', 'pending', 'waitinglist', 'canceled'):
        get_or_create(RegistrationStatus, name=name)
    db.session.commit()


@events.route('/')
def index():
    ''' Index page for the event registration, provides a list with links to
    the registrations for currently open events'''
    subquery = (
        db.session
        .query(EventRegistration.event_id, func.count('*').label('participants'))
        .filter_by(status='confirmed')
        .group_by(EventRegistration.event_id)
        .subquery()
    )
    query = (
        db.session.query(
            Event.id, Event.name, Event.description,
            Event.max_participants,
            func.coalesce(subquery.c.participants, 0).label('participants'),
        )
        .join(subquery, Event.id == subquery.c.event_id, isouter=True)
        .filter(Event.registration_open == True)
        .all()
    )

    events = []
    full_events = []
    for event in query:
        if event.max_participants and event.participants >= event.max_participants:
            full_events.append(event)
        else:
            events.append(event)

    return render_template('index.html', events=events, full_events=full_events)


@events.route('/<int:event_id>/registration/', methods=['GET', 'POST'])
def registration(event_id):
    event = Event.query.filter_by(id=event_id).first_or_404()

    n_participants = EventRegistration.query.filter_by(
        event_id=event.id, status='confirmed'
    ).count()
    if event.max_participants:
        free_places = event.max_participants - n_participants
        booked_out = free_places < 1
    else:
        free_places = None
        booked_out = False

    if not event.registration_open:
        if current_user.is_authenticated and current_user.has_access('view_registration'):
            flash(f'Vorschau! Die Anmeldung ist Offline.', 'warning')
        else:
            flash(f'Eine Anmeldung für "{event.name}" is derzeit nicht möglich', 'danger')
            return redirect(url_for('events.index'))

    form = create_wtf_form(
        event.registration_schema,
        additional_fields={
            'name': StringField('Name', [DataRequired()]),
            'email': create_email_field(event.force_tu_mail),
        }
    )

    if form.validate_on_submit():
        data = form.data
        email = data.pop('email')
        data.pop('csrf_token', None)

        try:
            validate(data, event.registration_schema)
        except ValidationError as e:
            flash(e.message, 'danger')
            return render_template('registration.html', form=form, event=event,
                                   registration=None)

        person, new_person = get_or_create(
            Person,
            email=email,
            defaults={'name': data['name']}
        )
        if new_person:
            db.session.commit()

        registration, new = get_or_create(
            EventRegistration,
            person_id=person.id,
            event_id=event.id,
            defaults={'data': data, 'status': 'pending'},
        )

        if not new:
            if registration.status == 'pending':
                flash(
                    render_template('pending.html', registration=registration),
                    category='danger'
                )
            elif registration.status == 'confirmed':
                flash(
                    render_template('registered.html', registration=registration),
                    category='danger'
                )
            elif registration.status == 'waitinglist':
                flash(
                    render_template('waiting.html', registration=registration),
                    category='danger'
                )
        else:
            flash('Um deine Registrierung abzuschließen, klicke auf den Bestätigungslink in der Email, die wir dir geschickt haben! Erst dann bist du angemeldet.', category='success')

            db.session.commit()
            send_registration_mail(registration)
        return redirect(url_for('events.index'))
    else:
        registration = None

    return render_template(
        'registration.html',
        form=form, event=event,
        registration=registration,
        booked_out=booked_out,
        free_places=free_places,
    )


def send_registration_mail(registration):
    event = registration.event
    person = registration.person
    ts = URLSafeSerializer(
        current_app.config["SECRET_KEY"],
        salt='registration-key',
    )
    token = ts.dumps(
        (person.id, registration.id),
    )
    if registration.status == 'pending':
        subject = 'Bestätige deine Anmeldung zu '
    else:
        subject = 'Bearbeite deine Anmeldung zu '

    send_email(
        subject=_(subject) + event.name,
        sender=current_app.config['MAIL_SENDER'],
        recipients=[person.email],
        body=render_template(
            'confirmation.txt',
            name=person.name,
            event=event.name,
            confirmation_link=ext_url_for('events.confirmation', token=token),
            submit_url=url_for('events.registration', event_id=event.id)
        )
    )


@events.route('/resend_email/', methods=['POST'])
def resend_email():
    registration_id = request.form['registration_id']

    registration = EventRegistration.query.get_or_404(registration_id)
    send_registration_mail(registration)
    flash('Email versendet', category='success')

    return redirect(url_for('events.index'))


@events.route('/<int:event_id>/')
def get_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return jsonify(status='No such event'), 404

    return jsonify(
        status='success',
        event=as_dict(event),
    )


@events.route('/<int:event_id>/participants/')
@access_required('get_participants')
def participants(event_id):
    event = Event.query.get(event_id)
    participants = (
        EventRegistration.query
        .filter_by(event_id=event_id)
        .order_by(EventRegistration.timestamp.is_(None), EventRegistration.timestamp)
    )

    if 'application/json' in request.headers.get('Accept'):
        return jsonify(
            status='success', participants=[as_dict(p) for p in participants],
        )

    return render_template(
        'participants.html', participants=participants, event=event
    )


@events.route('/registration/<token>/', methods=['GET', 'POST'])
def confirmation(token):
    ts = URLSafeSerializer(
        current_app.config["SECRET_KEY"],
        salt='registration-key',
    )
    try:
        person_id, registration_id = ts.loads(token)
    except BadData as e:
        print(e)
        abort(404)

    person = Person.query.get(person_id)
    registration = EventRegistration.query.get(registration_id)
    event = registration.event
    n_participants = EventRegistration.query.filter_by(event_id=event.id, status='confirmed').count()
    booked_out = event.max_participants and n_participants >= event.max_participants

    if registration.status == 'pending':
        if booked_out:
            registration.status = 'waitinglist'
            subject = 'Auf der Warteliste: '
            msg = 'Du befindest dich jetzt auf der Warteliste'
            category = 'warning'
        else:
            registration.status = 'confirmed'
            subject = 'Anmeldung bestätigt: '
            msg = 'Deine Anmeldung ist jetzt bestätigt'
            category = 'success'

        registration.timestamp = datetime.now(timezone.utc)

        db.session.add(registration)
        flash(msg, category)
        send_email(
            subject=_(subject) + registration.event.name,
            sender=current_app.config['MAIL_SENDER'],
            recipients=[person.email],
            body=render_template(
                'confirmed.txt',
                name=person.name,
                event=registration.event.name,
                edit_link=ext_url_for('events.confirmation', token=token),
            )
        )
        if event.notify_email:
            send_email(
                subject=f'Neue Anmeldung für "{event.name}"',
                sender=current_app.config['MAIL_SENDER'],
                recipients=[event.notify_email],
                body=render_template(
                    'notification.txt', person=person, event=event,
                    registration=registration,
                )
            )

    form = create_wtf_form(
        registration.event.registration_schema,
        additional_fields={
            'name': StringField('Name', [DataRequired()]),
            'email': EmailField('Email', [DataRequired()], render_kw={'disabled': ''})
        },
        data={**registration.data, 'email': person.email},
    )
    if form.validate_on_submit():
        data = form.data
        for key in ('email', 'csrf_token'):
            data.pop(key)

        registration.data = data
        flash('Anmeldung aktualisiert', 'success')

    form.submit.label.text = 'Speichern'
    db.session.commit()
    return render_template(
        'registration.html',
        form=form,
        event=registration.event,
        submit_url=url_for('events.confirmation', token=token),
        registration=registration,
    )
