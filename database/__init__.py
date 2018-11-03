from flask import Flask, jsonify, request
from flask_migrate import Migrate

from .config import Config
from .models import db, Person


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


def as_dict(instance):
    return {
        c.name: getattr(instance, c.name)
        for c in instance.__table__.columns
    }


@app.route('/persons', methods=['GET'])
def get_persons():
    persons = [as_dict(person) for person in Person.query.all()]
    return jsonify(status='success', persons=persons)


@app.route('/persons', methods=['POST'])
def add_person():
    data = request.get_json()
    if not data.get('name'):
        return jsonify(status='error', message='Mandatory parameter name missing'), 403
    if not data.get('email'):
        return jsonify(status='error', message='Mandatory parameter email missing'), 403
    p = Person(**data)
    db.session.add(p)
    db.session.commit()
    return jsonify(status='success')
