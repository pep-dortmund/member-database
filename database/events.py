from flask import Blueprint, render_template, abort, flash, redirect, url_for, jsonify
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField

from .models import db, Person, as_dict, Event, EventRegistration
from .utils import get_or_create
from .json_forms import create_wtf_form


events = Blueprint('events', __name__)


@events.route('/<int:event_id>/registration', methods=['GET', 'POST'])
def registration(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        abort(404)

    if not event.registration_open:
        flash(f'Eine Anmeldung für "{event.name}" is derzeit nicht möglich', 'danger')
        return redirect(url_for('index'))

    form = create_wtf_form(
        event.registration_schema,
        additional_fields={
            'name': StringField('Name', [DataRequired()]),
            'email': EmailField('Email', [DataRequired()])
        }
    )

    if form.validate_on_submit():
        person, _ = get_or_create(
            Person,
            email=form.email.data,
            defaults={'name': form.name.data}
        )
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
        'events/registration.html',
        form=form, event=event,
        url=f'/event/{event_id}/registration',
    )


@events.route('/<int:event_id>')
def get_event(event_id):
    event = Event.query.filter_by(id=event_id).first()
    if event is None:
        return jsonify(status='No such event'), 404

    return jsonify(
        status='success',
        event=as_dict(event),
    )
