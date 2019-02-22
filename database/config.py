import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.abspath('memberdb.sqlite')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # secret key is needed for sessions and tokens
    SECRET_KEY = os.environ['SECRET_KEY']

    # needed for url_for
    USE_HTTPS = os.getenv('USE_HTTPS', '').lower() == 'true'

    # config for the email server so this app can send mails
    MAIL_SENDER = os.environ['MAIL_SENDER']
    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = int(os.environ['MAIL_PORT'])
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', '').lower() == 'true'
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']

    # who gets a notification when there is a new membership application
    APPROVE_MAIL = os.environ['APPROVE_MAIL']
    ADMINS = os.environ['ADMINS'].split(',')

    TOKEN_MAX_AGE = os.environ.get('TOKEN_MAX_AGE', 30 * 60)  # 30 minutes default
