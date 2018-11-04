from flask import Flask, jsonify, request, url_for, abort, render_template
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
from functools import partial

from .config import Config
from .models import db, Person, as_dict
from .utils import get_or_create


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
mail = Mail(app)


ext_url_for = partial(
    url_for,
    _external=True,
    _scheme='https' if app.config['USE_HTTPS'] else 'http',
)


@app.route('/persons', methods=['GET'])
def get_persons():
    persons = [as_dict(person) for person in Person.query.all()]
    return jsonify(status='success', persons=persons)


@app.route('/persons', methods=['POST'])
def add_person():
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
    members = Person.query.filter_by(member=True, member_approved=True).all()
    persons = [as_dict(member) for member in members]
    return jsonify(status='success', persons=persons)


@app.route('/members', methods=['POST'])
def add_member():
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
    
    p.member = True
    db.session.add(p)
    db.session.commit()
    
    msg = Message(
        'Neuer Mitgliedsantrag',
        sender=app.config['MAIL_SENDER'],
        recipients=[app.config['APPROVE_MAIL']],
    )
    msg.body = render_template(
        'approve_member.txt',
        new_member=p,
        url=ext_url_for('applications'),
    )
    mail.send(msg)

    return jsonify(status='success')


@app.route('/request_edit', methods=['POST'])
def send_edit_token():
    email = request.form['email']

    p = Person.query.filter_by(email=email).first()
    if p is None:
        return jsonify(status='error', message='No such person'), 422

    token = ts.dumps(email, salt='recover-key')

    msg = Message(
        'PeP et al. e.V. Mitgliedsdatenänderung',
        sender=app.config['MAIL_SENDER'],
        recipients=[email],
    )
    msg.body = render_template(
        'edit_mail.txt',
        edit_link=ext_url_for('edit', token=token),
    )
    mail.send(msg)

    return jsonify(status='success', message='Edit mail sent.')


@app.route('/edit/<token>')
def edit(token):
    pass


@app.route('/edit/<token>', methods=['POST'])
def save_edit(token):
    pass


@app.route('/applications')
def applications():
    pass
