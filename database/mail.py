from flask import current_app
from flask_mail import Mail, Message
from threading import Thread
import socket

socket.setdefaulttimeout(30)
mail = Mail()


def send_async_email(app, msg):
    '''
    Function to be called from a Thread to send msg in backoground.
    See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    '''
    app.logger.info(f'Sending mail with subject "{msg.subject}" to {msg.recipients}')
    with app.app_context():
        mail.send(msg)


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
        # See https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure
        # For an explanation of the current_app magic
        Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()
