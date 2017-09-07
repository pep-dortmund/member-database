from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from mongoengine import connect

from .db import MemberDatabase
from .member import Member

db = MemberDatabase('pep-test', reset=True)

app = Flask(__name__)
app.secret_key = 'not secret'

admin = Admin(app, name='database', template_mode='bootstrap3', url='')
admin.add_view(ModelView(Member))

@app.route('/')
def index():
    return 'Hello World!'
