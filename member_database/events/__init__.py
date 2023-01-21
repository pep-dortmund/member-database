from flask import (
    Blueprint, render_template, abort, flash, redirect, url_for, jsonify, current_app,
    request,
)
from flask_cors import cross_origin
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_mail import Attachment
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp
from wtforms.fields import EmailField
from itsdangerous import URLSafeSerializer, BadData
from flask_babel import _
from jsonschema import validate, ValidationError
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
import logging

from ..models import db, Person, as_dict
from ..utils import get_or_create, ext_url_for
from ..mail import send_email
from ..authentication import access_required

from .models import Event, EventRegistration, RegistrationStatus
from .json_forms import create_wtf_form
from .forms import SendMailForm


__all__ = [
    'events',
    'Event', 'EventRegistration', 'RegistrationStatus',
]

log = logging.getLogger(__name__)
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
        .filter_by(status_name='confirmed')
        .group_by(EventRegistration.event_id)
        .subquery()
    )
    query = (
        db.session.query(
            Event.id, Event.name, Event.description,
            Event.max_participants, Event.registration_open,
            func.coalesce(subquery.c.participants, 0).label('n_participants'),
        )
        .join(subquery, Event.id == subquery.c.event_id, isouter=True)
    )

    # for logged in users, we want to show all events, all others
    # only get to see the ones that are currently open
    if not current_user.is_authenticated:
        query = query.filter(Event.registration_open == True)

    query = query.all()

    events = []
    full_events = []
    closed_events = []
    for event in query:
        if not event.registration_open:
            closed_events.append(event)
        elif event.max_participants and event.n_participants >= event.max_participants:
            full_events.append(event)
        else:
            events.append(event)

    return render_template('events/index.html', events=events, full_events=full_events, closed_events=closed_events)


def get_free_places(event):
    n_participants = EventRegistration.query.filter_by(
        event_id=event.id, status_name='confirmed'
    ).count()
    if event.max_participants:
        return event.max_participants - n_participants
    return None


@events.route('/<int:event_id>/registration/', methods=['GET', 'POST'])
def registration(event_id):
    event = Event.query.filter_by(id=event_id).first_or_404()

    free_places = get_free_places(event)
    if free_places is not None:
        booked_out = free_places < 1
    else:
        booked_out = False

    if not event.registration_open:
        if current_user.is_authenticated and current_user.has_access('view_registration'):
            flash(f'Vorschau! Die Anmeldung ist Offline.', 'warning')
        else:
            flash(f'Eine Anmeldung für "{event.name}" is derzeit nicht möglich', 'danger')
            return redirect(url_for('events.index'))

    Form = create_wtf_form(
        event.registration_schema,
        additional_fields={
            'name': StringField('Name', [DataRequired()]),
            'email': create_email_field(event.force_tu_mail),
        }
    )
    form = Form()

    if form.validate_on_submit():
        data = form.data
        email = data.pop('email')
        data.pop('csrf_token', None)

        try:
            validate(data, event.registration_schema)
        except ValidationError as e:
            flash(e.message, 'danger')
            return render_template('events/registration.html', form=form,
                                   event=event)

        person, new_person = get_or_create(
            Person,
            email=email,
            defaults={'name': data['name']}
        )
        if new_person:
            log.info(f'Created new person {person}')
            db.session.commit()

        registration, new = get_or_create(
            EventRegistration,
            person_id=person.id,
            event_id=event.id,
            defaults={'data': data, 'status_name': 'pending'},
        )

        if not new:
            if registration.status_name == 'pending':
                flash(
                    render_template('events/pending.html', registration=registration),
                    category='danger'
                )
            elif registration.status_name == 'confirmed':
                flash(
                    render_template('events/registered.html', registration=registration),
                    category='danger'
                )
            elif registration.status_name == 'waitinglist':
                flash(
                    render_template('events/waiting.html', registration=registration),
                    category='danger'
                )
        else:
            log.info(f'New registration for {event} by {person}')
            flash('Um deine Registrierung abzuschließen, klicke auf den Bestätigungslink in der Email, die wir dir geschickt haben! Erst dann bist du angemeldet.', category='success')

            db.session.commit()
            send_registration_mail(registration)
        return redirect(url_for('events.index'))
    else:
        registration = None

    return render_template(
        'events/registration.html',
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
    
    edit = registration.status_name != 'pending'
    if not edit:
        subject = 'Bestätige deine Anmeldung zu '
    else:
        subject = 'Bearbeite deine Anmeldung zu '

    send_email(
        subject=_(subject) + event.name,
        sender=current_app.config['MAIL_SENDER'],
        recipients=[person.email],
        body=render_template(
            'events/confirmation.txt',
            name=person.name,
            event=event.name,
            confirmation_link=ext_url_for('events.confirmation', token=token),
            submit_url=url_for('events.registration', event_id=event.id),
            cancel_link=ext_url_for("events.cancel", token=token),
            edit=edit
        )
    )


@events.route('/cancel/<token>/', methods=['GET', 'POST'])
def cancel(token):
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
    registration = EventRegistration.query.get_or_404(registration_id)
    
    class CancelForm(FlaskForm):
        submit = SubmitField(f'{person.name} ({person.email}) von {registration.event.name} abmelden.')

    form = CancelForm()
    if form.validate_on_submit():
        if not registration.event.registration_open:
            flash('Abmelden nicht möglich. Veranstaltung schon vorbei.', category='danger')
            return redirect(url_for('events.index'))

        # Delete registration
        db.session.delete(registration)
        db.session.commit()
        flash('Von Veranstaltung abgemeldet.', category='success')
        return redirect(url_for('events.index'))
    else:
        return render_template('events/cancel.html', form=form)


@events.route('/resend_email/', methods=['POST'])
def resend_email():
    registration_id = request.form['registration_id']

    registration = EventRegistration.query.get_or_404(registration_id)
    send_registration_mail(registration)
    flash('Email versendet', category='success')

    return redirect(url_for('events.index'))


@events.route('/resend_emails/', methods=['GET', 'POST'])
def resend_emails():
    '''Resend all emails for open events for a given email address'''

    class ResendForm(FlaskForm):
        email = EmailField(validators=[DataRequired()])
        submit = SubmitField('Emails für aktuelle Anmeldungen erneut versenden.')

    form = ResendForm()

    if form.validate_on_submit():
        email = request.form['email']
        person = Person.query.filter_by(email=email).first()
        if person is None:
            flash(f'Keine Veranstaltungs-Anmeldung für "{email}"', 'danger')
            return redirect(url_for('events.index'))

        open_registrations = list(
            EventRegistration.query
            .filter_by(person=person)
            .join(Event)
            .filter_by(registration_open=True)
        )

        if len(open_registrations) == 0:
            flash(f'Keine Veranstaltungs-Anmeldung für "{email}"', 'danger')

        for registration in open_registrations:
            send_registration_mail(registration)
        flash('Emails versendet', category='success')

        return redirect(url_for('events.index'))

    else:
        return render_template('events/resend_emails.html', form=form)


@events.route('/<int:event_id>/')
@cross_origin(origins=["https://([a-z]+.)?pep-dortmund.(org|de)"])
def get_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return jsonify(status_name='No such event'), 404

    evt_info = as_dict(event)
    evt_info['free_places'] = get_free_places(event)

    return jsonify(
        status_name='success',
        event=evt_info,
    )


@events.route('/<int:event_id>/participants/')
@access_required('get_participants')
def participants(event_id):
    event = Event.query.get(event_id)
    participants = (
        EventRegistration.query
        .options(joinedload(EventRegistration.person))  # directly fetch persons
        .filter_by(event_id=event_id)
        .order_by(EventRegistration.timestamp.is_(None), EventRegistration.timestamp)
    )

    if 'application/json' in request.headers.get('Accept'):
        data = []
        for p in participants:
            d = as_dict(p)
            # fill email from person if not present in data
            d['data']['email'] = d['data'].get('email', p.person.email)
            data.append(d)

        return jsonify(
            status_name='success', participants=data,
        )

    return render_template(
        'events/participants.html', participants=participants, event=event
    )


@events.route('/<int:event_id>/write_mail/', methods=['GET', 'POST'])
@access_required('write_email')
def write_mail(event_id):
    event = Event.query.get(event_id)

    form = SendMailForm(name=current_user.person.name, email=current_user.person.email)
    n_participants = EventRegistration.query.filter_by(event_id=event_id, status_name="confirmed").count()

    if n_participants == 0:
        flash(f'No participants yet for event {event.name}', 'danger')
        return redirect(url_for('events.index'))

    if form.validate_on_submit():
        participants = (
            EventRegistration.query
            .options(joinedload(EventRegistration.person))  # directly fetch persons
            .filter_by(event_id=event_id, status_name="confirmed")
        )

        attachments = [
            Attachment(
                filename=f.filename,
                data=f.read(),
                content_type=f.mimetype,
            )
            for f in request.files.getlist(form.attachments.name)
        ]

        # send to everyone in bcc
        bcc = [f'{p.person.name} <{p.person.email}>' for p in participants]
        reply_to = f'{form.name.data} <{form.email.data}>'
        send_email(
            sender=current_app.config['MAIL_SENDER'],
            subject=form.subject.data,
            recipients=[reply_to],
            bcc=bcc,
            body=form.body.data,
            reply_to=reply_to,
            attachments=attachments,
        )

        flash('Mail send', 'success')
        return redirect(url_for('events.index'))

    return render_template(
        'events/write_mail.html', event=event, form=form,
        n_participants=n_participants
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
    n_participants = EventRegistration.query.filter_by(event_id=event.id, status_name='confirmed').count()
    booked_out = event.max_participants and n_participants >= event.max_participants

    log.info(f'Confirmation for {event} by {person} ({registration})')

    if registration.status_name == 'pending':
        if booked_out:
            registration.status_name = 'waitinglist'
            subject = 'Auf der Warteliste: '
            msg = 'Du befindest dich jetzt auf der Warteliste'
            category = 'warning'
        else:
            registration.status_name = 'confirmed'
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
                'events/confirmed.txt',
                name=person.name,
                event=registration.event.name,
                edit_link=ext_url_for('events.confirmation', token=token),
                cancel_link=ext_url_for('events.cancel', token=token)
            )
        )
        if event.notify_email:
            send_email(
                subject=f'Neue Anmeldung für "{event.name}"',
                sender=current_app.config['MAIL_SENDER'],
                recipients=[event.notify_email],
                body=render_template(
                    'events/notification.txt', person=person, event=event,
                    registration=registration,
                )
            )

    Form = create_wtf_form(
        registration.event.registration_schema,
        additional_fields={
            'name': StringField('Name', [DataRequired()]),
            'email': EmailField('Email', [DataRequired()], render_kw={'disabled': ''})
        },
    )
    form = Form(data={**registration.data, 'email': person.email})

    if form.validate_on_submit():
        data = form.data
        for key in ('email', 'csrf_token'):
            data.pop(key)

        registration.data = data
        flash('Anmeldung aktualisiert', 'success')

    form.submit.label.text = 'Speichern'
    db.session.commit()
    return render_template(
        'events/registration.html',
        form=form,
        event=registration.event,
        submit_url=url_for('events.confirmation', token=token),
        registration=registration,
    )
