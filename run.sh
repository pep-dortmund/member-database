#! /bin/sh

# apply database migrations
flask db upgrade

# start the server
gunicorn --bind 0.0.0.0:$PORT "member_database:create_app()"
