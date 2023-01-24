from flask import flash, abort, request, jsonify
from flask_login import LoginManager, login_required, current_user, AnonymousUserMixin
import base64

from functools import wraps

from .models import User, get_user_by_name_or_email


login = LoginManager()

ACCESS_LEVELS = set()


class AnonymousUser(AnonymousUserMixin):
    """
    Adds `has_access` method always returning false to the anonymous_user
    """

    @staticmethod
    def has_access(access):
        return False


def access_required(name):
    """
    Check if current_user has a role with access_level named `name`.
    Abort request with 401, if that's not the case.

    Usage:
        Decorate view function (`app.route(...)`) with this decorator and
        specify a name of an access_level. The name will be compared to
        all access_levels of all rules of the current_user.
    """
    # register access level,
    # so it can be inserted into the database @first_request
    ACCESS_LEVELS.add(name)

    def access_decorator(func):
        @wraps(func)
        @login_required  # first of all, a user needs to be logged in
        def decorated_function(*args, **kwargs):
            if not current_user.has_access(name):
                flash(
                    f'Your user does not have the access level "{name}"'
                    " required to view this page.",
                    category="danger",
                )
                abort(401)

            return func(*args, **kwargs)

        return decorated_function

    return access_decorator


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.request_loader
def load_user_from_request(request):

    basic_auth = request.headers.get("Authorization")

    if basic_auth:
        basic_auth = basic_auth.replace("Basic ", "", 1)
        try:
            basic_auth = base64.b64decode(basic_auth)
            user, password = basic_auth.decode().split(":")
        except (TypeError, ValueError):
            # a failed attempt should take as long
            # as a successfull one, thus we do not exit early
            # but perform the database request anyway
            user = None
            password = ""

        user = get_user_by_name_or_email(user)

        if user and user.check_password(password) is True:
            return user

    return None


@login.unauthorized_handler
def handle_needs_login():
    if "application/json" in request.headers.get("Accept", []):
        return jsonify(status="access_denied"), 401

    flash("You have to be logged in to access this page.", category="danger")
    abort(401)
