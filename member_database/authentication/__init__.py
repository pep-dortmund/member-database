from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer

from ..mail import send_email
from ..models import db
from ..utils import ext_url_for, get_or_create, table_exists
from .forms import LoginForm, PasswordResetForm, SendPasswordResetForm
from .login import (
    ACCESS_LEVELS,
    AnonymousUser,
    access_required,
    handle_needs_login,
    login,
)
from .models import AccessLevel, Role, User, get_user_by_name_or_email

__all__ = [
    "auth",
    "login",
    "access_required",
    "AnonymousUser",
    "AccessLevel",
    "Role",
    "User",
    "get_user_by_name_or_email",
    "handle_needs_login",
]

login.anonymous_user = AnonymousUser


auth = Blueprint("auth", __name__, template_folder="templates")


def init_authentication_database():
    if not table_exists(AccessLevel):
        current_app.logger.info(
            "Skipping auth db init as table does not exist (run flask db upgrade)"
        )
        return

    for access_level in ACCESS_LEVELS:
        get_or_create(AccessLevel, id=access_level)
    db.session.commit()


@auth.route("/login/", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.is_submitted():
        if form.validate_on_submit():
            user = get_user_by_name_or_email(form.user_or_email.data)

            if user is None or not user.check_password(form.password.data):
                flash("Invalid user or password", "danger")
                abort(401)

            login_user(user)
            return redirect(request.args.get("next") or url_for("main.index"))

        else:
            # if form was posted but is not valid we abort with 401
            abort(401)

    return render_template("authentication/login_form.html", title="Login", form=form)


@auth.route("/password_reset/", methods=["GET", "POST"])
def send_password_reset():
    form = SendPasswordResetForm()

    if form.validate_on_submit():
        user = get_user_by_name_or_email(form.user_or_email.data)
        if user is None:
            flash("Unknown username or email", "danger")
            return redirect(url_for("auth.send_password_reset"))

        send_password_reset_mail(user.person)

        flash("Password reset email sent", "success")
        return redirect("/")

    return render_template("simple_form.html", title="Reset Password", form=form)


@auth.route("/password_reset/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:
        email = load_reset_token(token)
    except SignatureExpired:
        flash("Password reset link expired, request a new one", "danger")
        return redirect("/")
    except BadData:
        abort(404)

    form = PasswordResetForm()
    if form.validate_on_submit():
        user = get_user_by_name_or_email(email)
        user.set_password(form.new_password.data)
        db.session.add(user)
        db.session.commit()
        return redirect("/")

    return render_template("simple_form.html", title="Reset Password", form=form)


@auth.route("/logout/", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("main.index"))


def send_password_reset_mail(person):
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(person.email, salt="password-reset")

    link = ext_url_for("auth.reset_password", token=token)

    send_email(
        subject="Password reset for registration.pep-dortmund.org",
        recipients=[f"{person.name} <{person.email}>"],
        sender=current_app.config["MAIL_SENDER"],
        body=render_template("mail/reset_password.html", reset_link=link),
    )


def load_reset_token(token):
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return ts.loads(token, salt="password-reset", max_age=10 * 60)
