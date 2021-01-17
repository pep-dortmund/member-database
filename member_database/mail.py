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
    log.error((
        'Sending email failed in {tries} attempt'
        ', waiting {wait:.1f} s.'
    ).format(**details))


@backoff.on_exception(
    backoff.expo,
    (ConnectionError, OSError),  # all socket exceptions are subclasses of OSError
    max_tries=12,                # max waiting time: 1.4 days
    on_backoff=on_backoff,
    base=2,                      # double waiting time after each try
    factor=30,                   # 30, 60, 120 ... seconds
)
def target(app, msg):
    log.info(f'Sending mail with subject "{msg.subject}" to {msg.recipients}')
    with app.app_context():
        try:
            mail.send(msg)
        except Exception:
            log.exception(
                f'Failed sending mail with subject "{msg.subject}" to {msg.recipients}'
            )
            raise
    log.info(f'Mail "{msg.subject}" sent to {msg.recipients}')


def send_msg_async(msg):
    '''
    Calls a mail.send(msg) in a background thread.
    Retries on errors using exponential backoff.
    See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    '''
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
