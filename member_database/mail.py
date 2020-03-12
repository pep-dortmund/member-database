from flask import current_app
from flask_mail import Mail, Message
from threading import Thread
import socket
import logging
import backoff


log = logging.getLogger(__name__)

socket.setdefaulttimeout(30)
mail = Mail()


def send_msg_async(msg):
    '''
    Calls a mail.send(msg) in a background thread.
    Retries on errors using exponential backoff.
    See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    '''
    def on_backoff(details):
        log.error('Sending email failed in {tries} attempt, waiting {wait:.1f} s.')

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=18,
        on_backoff=on_backoff,
    )
    def target(app, mail):
        log.info(f'Sending mail with subject "{msg.subject}" to {msg.recipients}')
        with app.app_context():
            try:
                mail.send(msg)
            except Exception:
                logging.exception('Failed sending mail')
                raise
        log.info('Mail sent')

    # See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
    # For an explanation of the current_app magic
    Thread(
        target=target,
        args=(current_app._get_current_object(), msg)
    ).start()


def send_email(subject, sender, recipients, body, **kwargs):
    '''
    Send an email async using a background thread
    '''
    msg = Message(subject=subject, sender=sender, recipients=recipients, **kwargs)
    msg.body = body

    # capturing mails does not work in another thread
    # so just send it here for the unit tests
    if current_app.config['TESTING']:
        mail.send(msg)
    elif current_app.config['DEBUG'] is True:
        print(body)
    else:
        send_msg_async(msg)
