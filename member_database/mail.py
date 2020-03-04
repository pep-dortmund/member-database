from flask import current_app
from flask_mail import Mail, Message
from threading import Thread
import socket
import logging
import backoff


log = logging.getLogger(__name__)

socket.setdefaulttimeout(30)
mail = Mail()


def on_backoff(details):
    log.error('Sending email failed in {tries} attempt, waiting {wait:.1f} s.')


@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=18,
    on_backoff=on_backoff,
)
def send_mail(app, msg):
    '''
    Function to be called from a Thread to send msg in backoground.
    See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    '''
    log.info(f'Sending mail with subject "{msg.subject}" to {msg.recipients}')
    try:
        with app.app_context():
            mail.send(msg)
    except Exception:
        logging.exception('Failed sending mail')
        raise
    log.info('Mail sent')


def send_email(subject, sender, recipients, body, **kwargs):
    '''
    Send an email async using a background thread
    '''
    msg = Message(subject=subject, sender=sender, recipients=recipients, **kwargs)
    msg.body = body

    # capturing mails does not work in another thread
    # so just send it here for the unit tests
    if current_app.config['TESTING']:
        send_mail(current_app._get_current_object(), msg)
    elif current_app.config['DEBUG'] is True:
        print(body)
    else:
        # See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
        # For an explanation of the current_app magic
        Thread(
            target=send_email,
            args=(current_app._get_current_object(), msg)
        ).start()
