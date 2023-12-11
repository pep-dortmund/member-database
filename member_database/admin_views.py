import json

from flask import abort
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import fields
from flask_login import current_user
from wtforms.fields import PasswordField

from .authentication import ACCESS_LEVELS, AccessLevel, Role, User, handle_needs_login
from .events import Event, EventRegistration
from .models import Person, TUStatus, db


class PrettyJSONField(fields.JSONField):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data:
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        else:
            return ""


class IndexView(AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return handle_needs_login()
        return super().index()


class AuthorizedView(ModelView):
    access_level = None
    can_set_page_size = True
    can_view_details = True
    details_modal = True

    def __init_subclass__(cls):
        """Add a subclasses access level to the set of access levels"""
        ACCESS_LEVELS.add(cls.access_level)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_access(
            self.access_level
        )

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            # we have a user, bot insufficient access
            abort(401)
        else:
            # let user login
            return handle_needs_login()


class EventView(AuthorizedView):
    access_level = "event_admin"
    column_list = [
        "name",
        "notify_email",
        "max_participants",
        "force_tu_mail",
        "registration_open",
        "shortlink",
    ]
    column_filters = [
        "name",
        "max_participants",
        "force_tu_mail",
        "registration_open",
        "notify_email",
    ]
    form_excluded_columns = ["registrations"]
    column_editable_list = ["name", "registration_open", "shortlink"]
    column_descriptions = {
        "description": "Description shown above on the registration page. HTML is allowed in this field.",
        "footer": "Additional text to be shown below the form on the registration page. HTML is allowed in this field.",
        "shortlink": 'Makes event available via "events/{shortlink}".',
    }
    form_widget_args = {
        "description": {
            "rows": 10,
            "style": "width: 100%; font-family: monospace;",
        },
        "registration_schema": {
            "rows": 16,
            "style": "width: 100%; font-family: monospace;",
        },
    }
    form_overrides = {"registration_schema": PrettyJSONField}


class RoleView(AuthorizedView):
    column_display_pk = True
    column_list = ["id", "access_levels", "users"]
    form_columns = ["id", "access_levels", "users"]
    access_level = "role_admin"


class AccessLevelView(AuthorizedView):
    column_display_pk = True
    column_list = ["id", "roles"]
    form_columns = ["id", "roles"]
    access_level = "access_level_admin"


class EventRegistrationView(AuthorizedView):
    access_level = "event_registration_admin"
    column_filters = [
        Event.id,
        Event.name,
        Person.email,
        Person.membership_status_id,
    ]

    form_columns = [
        "id",
        "event",
        "person",
        "status",
        "data",
        "timestamp",
    ]


class PersonView(AuthorizedView):
    access_level = "person_admin"
    column_list = [
        "name",
        "email",
        "user",
        "event_registrations",
        "membership_status",
        "joining_date",
    ]
    column_filters = ["name", "email", Person.membership_status_id]


class TUStatusView(AuthorizedView):
    access_level = "person_admin"


class UserView(AuthorizedView):
    access_level = "user_admin"
    column_list = ["username", "person", "roles"]
    column_filters = ["username", Person.email]
    form_excluded_columns = ["password_hash"]
    form_extra_fields = {
        "new_password": PasswordField("New Password"),
    }

    def on_model_change(self, form, user, is_created):
        if form.new_password.data is not None:
            user.set_password(form.new_password.data)


def create_admin_views():
    admin = Admin(
        index_view=IndexView(),
        template_mode="bootstrap4",
        base_template="admin_master.html",
    )
    admin.add_view(EventView(Event, db.session))
    admin.add_view(EventRegistrationView(EventRegistration, db.session))
    admin.add_view(PersonView(Person, db.session))
    admin.add_view(UserView(User, db.session))
    admin.add_view(RoleView(Role, db.session))
    admin.add_view(AccessLevelView(AccessLevel, db.session))
    admin.add_view(TUStatusView(TUStatus, db.session))
    return admin
