from datetime import date
from re import M
from flask import (
    jsonify, request, url_for, render_template, redirect,
    flash, abort, Blueprint, current_app
)
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData

from sqlalchemy.exc import IntegrityError

from .models import db, Person, as_dict
from .models.person import AccessLevel, MembershipStatus
from .queries import get_user_by_name_or_email
from .utils import get_or_create, ext_url_for
from .authentication import (
    access_required,
    LoginForm,
    PasswordResetForm,
    SendPasswordResetForm,
    send_password_reset_mail,
    load_reset_token,
    ACCESS_LEVELS,
)
from .forms import PersonEditForm, MembershipForm, RequestLinkForm
from .mail import send_email


main = Blueprint('main', __name__)


@main.before_app_first_request
def init_database():
    for access_level in ACCESS_LEVELS:
        get_or_create(AccessLevel, id=access_level)

    for name in MembershipStatus.STATES:
        get_or_create(MembershipStatus, id=name)

    db.session.commit()


@main.route('/')
def index():
    return render_template('index.html')


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


@main.route('/members/', methods=['GET'])
@access_required('get_members')
def get_members():
    '''Return a json list with all current members'''
    members = Person.query.filter_by(membership_status_id=MembershipStatus.CONFIRMED).all()
    members = [as_dict(member) for member in members]
    return jsonify(status='success', members=members)


@main.route('/register/', methods=['GET', 'POST'])
def register():
    '''
    Endpoint for membership registration.

    Simple form to sign up to the club, only requiring name and email.

    After a request has been made, the applicant has to confirm their email.
    After the email was confirmed, the board gets notified that a new application
    was made and can accept/deny it.
    '''

    form = MembershipForm()

    if form.validate_on_submit():
        p, _new = get_or_create(
            Person,
            email=form.email.data,
            defaults={'name': form.name.data},
        )

        if p.membership_status_id == MembershipStatus.DENIED:
            flash(
                'Du hast bereits einen Mitgliedsantrag eingereicht, der abgelehnt wurde.'
                ' Bitte kontaktiere uns, falls du dies für einen Irrtum hälst.'
            )
            return redirect(url_for('main.index'))

        if p.membership_status_id == MembershipStatus.EMAIL_UNVERIFIED:
            flash(
                'Du hast bereits einen Mitgliedsantrag eingereicht,'
                ' aber deine Email noch nicht bestätigt.'
                f' Wir haben die Bestätigungsemail erneut an {p.email} versendet.',
                category='warning',
            )

        if p.membership_status_id == MembershipStatus.PENDING:
            flash(
                'Du hast bereits einen Mitgliedsantrag eingereicht,'
                ' aber dieser ist noch nicht vom Vorstand bestätigt worden.'
                ' Dies kann ein paar Tage dauern.',
                category='info',
            )
            return redirect(url_for('main.index'))

        if p.membership_status_id == MembershipStatus.CONFIRMED:
            flash('Du bist bereits Mitglied', category='danger')
            return redirect(url_for('main.index'))

        p.membership_status_id = MembershipStatus.EMAIL_UNVERIFIED
        db.session.add(p)
        db.session.commit()

        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = ts.dumps(p.email, salt='edit-key')

        send_email(
            subject=_('PeP et al. Mitgliedsantrag: Email bestätigen'),
            sender=current_app.config['MAIL_SENDER'],
            recipients=[p.email],
            body=render_template(
                'mail/verify.txt',
                new_member=p,
                url=ext_url_for('main.edit', token=token),
            )
        )

        max_age = current_app.config['TOKEN_MAX_AGE'] // 60
        flash(
            'Um den Vorgang abzuschließen, klicke auf den Link in der'
            ' Bestätigungsemail. Vorher können wir deinen Antrag'
            f' nicht bearbeiten. Der Link ist {max_age} Minuten gültig.',
            category='warning',
        )
        return redirect(url_for('main.index'))

    return render_template(
        'simple_form.html', title='Mitgliedsantrag', form=form
    )


@main.route('/request_edit', methods=['POST', 'GET'])
def request_edit():
    '''
    Request a link to edit personal data
    '''
    form = RequestLinkForm()

    if form.validate_on_submit():
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = ts.dumps(form.email.data, salt='edit-key')

        send_email(
            subject=_('PeP et al. e.V. Mitgliedsdatenänderung'),
            sender=current_app.config['MAIL_SENDER'],
            recipients=[form.email.data],
            body=render_template(
                'mail/edit_mail.txt',
                edit_link=ext_url_for('main.edit', token=token),
            )
        )
        flash('E-Mail mit Link für die Datenänderung verschickt', 'success')
        return redirect(url_for('main.index'))

    return render_template(
        'simple_form.html',
        form=form,
        title='Persönliche Daten ändern',
    )


@main.route('/request_gdpr_data', methods=['POST', 'GET'])
def request_gdpr_data():
    '''
    Request a link to view personal data
    '''
    form = RequestLinkForm()

    if form.validate_on_submit():
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = ts.dumps(form.email.data, salt='request_gdpr_data-key')

        send_email(
            subject='PeP et al. e.V. - Einsicht in gespeicherte Daten',
            sender=current_app.config['MAIL_SENDER'],
            recipients=[form.email.data],
            body=render_template(
                'mail/request_data_mail.txt',
                data_link=ext_url_for('main.view_data', token=token),
            )
        )
        flash('E-Mail mit Link für die Dateneinsicht verschickt', 'success')
        return redirect(url_for('main.index'))

    return render_template(
        'simple_form.html',
        form=form,
        title='Meine gespeicherten Daten einsehen (DSGVO-Anfrage)',
    )

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
        flash(_('Ihre Sitzung ist abgelaufen'), category='danger')
        return redirect(url_for('main.index'))
    except BadData:
        abort(404)

    p = Person.query.filter_by(email=email).first()
    if p is None:
        abort(404)

    if p.membership_status_id == MembershipStatus.EMAIL_UNVERIFIED:
        send_email(
            subject='Neuer Mitgliedsantrag',
            sender=current_app.config['MAIL_SENDER'],
            recipients=[current_app.config['APPROVE_MAIL']],
            body=render_template(
                'mail/approve_member.txt',
                new_member=p,
                url=ext_url_for('main.applications'),
            )
        )

        p.membership_status_id = MembershipStatus.PENDING
        p.email_valid = True

        db.session.add(p)
        db.session.commit()
        flash(_('Email erfolgreich bestätigt'), category="success")

    if p.membership_status_id == MembershipStatus.PENDING:
        flash(
            _('Dein Mitgliedsantrag wartet auf Bestätigung durch den Vorstand'),
            category="info",
        )

    form = PersonEditForm(
        name=p.name,
        email=p.email,
        date_of_birth=p.date_of_birth,
        joining_date=p.joining_date,
        membership_status=p.membership_status_id,
    )

    if form.validate_on_submit():
        p.name = form.name.data
        if p.email != form.email.data:
            p.email_valid = False
            p.email = form.email.data
        p.date_of_birth = form.date_of_birth.data
        db.session.commit()
        flash(_('Ihre Daten wurden erfolgreich aktualisiert.'))
        return redirect(url_for('main.edit', token=token))

    return render_template('edit.html', form=form)


@main.route('/view_data/<token>')
def view_data(token):
    try:
        ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        email = ts.loads(token, salt='request_gdpr_data-key')
    except SignatureExpired:
        flash(_('Ihre Sitzung ist abgelaufen'))
    except BadData:
        abort(404)

    p = Person.query.filter_by(email=email).first()

    if p is None:
        abort(404)

    personal_data = as_dict(p)
    personal_data['event_registrations'] = []

    for reg in p.event_registrations:
        personal_data['event_registrations'].append({
            'event': as_dict(reg.event),
            'registration': as_dict(reg)
        })

    return jsonify(status='success', personal_data=personal_data)


@main.route('/applications')
@access_required('member_management')
def applications():
    applications = Person.query.filter_by(membership_status_id="pending").all()
    return render_template('applications.html', applications=applications)


@main.route('/applications/<int:person_id>/', methods=['POST'])
@access_required('member_management')
def handle_application(person_id):
    application = (
        Person.query
        .filter_by(id=person_id, membership_status_id="pending")
        .one_or_none()
    )

    if application is None:
        flash("Kein offener Mitgliedsantrag für diese Person", category="danger")
        abort(404)

    decision = request.form.get('decision')
    if decision == "accept":
        application.joining_date = date.today()
        db.session.add(application)
        db.session.commit()

        flash(f"Mitgliedsantrag für {application.name} angenommen", category="success")
        send_email(
            subject=_('Willkommen bei PeP et al. e.V.'),
            sender=current_app.config['MAIL_SENDER'],
            recipients=[application.email],
            body=render_template(
                'mail/welcome.txt',
                new_member=application,
            )
        )
        application.membership_status_id = MembershipStatus.CONFIRMED
    elif decision == 'deny':
        flash(f"Mitgliedsantrag für {application.name} abgelehnt", category="danger")
        application.membership_status_id = MembershipStatus.DENIED
    else:
        abort(400)

    db.session.add(application)
    db.session.commit()

    return redirect(url_for("main.applications"))


@main.route('/login/', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user_by_name_or_email(form.user_or_email.data)

            if user is None or not user.check_password(form.password.data):
                flash('Invalid user or password', 'danger')
                abort(401)

            login_user(user)
            return redirect(request.args.get('next') or url_for('main.index'))

        else:
            # if form was posted but is not valid we abort with 401
            abort(401)

    return render_template('simple_form.html', title='Login', form=form)


@main.route('/password_reset/', methods=['GET', 'POST'])
def send_password_reset():
    form = SendPasswordResetForm()

    if form.validate_on_submit():
        user = get_user_by_name_or_email(form.user_or_email.data)
        if user is None:
            flash('Unknown username or email', 'danger')
            return redirect(url_for('main.send_password_reset'))

        send_password_reset_mail(user.person)

        flash('Password reset email sent', 'success')
        return redirect('/')

    return render_template(
        'simple_form.html', title='Reset Password', form=form
    )


@main.route('/password_reset/<token>', methods=['GET', 'POST'])
def reset_password(token):

    try:
        email = load_reset_token(token)
    except SignatureExpired:
        flash('Password reset link expired, request a new one', 'danger')
        return redirect('/')
    except BadData:
        abort(404)

    form = PasswordResetForm()
    if form.validate_on_submit():
        user = get_user_by_name_or_email(email)
        user.set_password(form.new_password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

    return render_template(
        'simple_form.html', title='Reset Password', form=form
    )


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))
