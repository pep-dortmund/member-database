import json

from flask import redirect, request, url_for
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import fields


class PrettyJSONField(fields.JSONField):
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data:
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        else:
            return ''


class AuthorizedView(ModelView):
    access_level = None

    def is_accessible(self):
        if current_user is not None:
            return current_user.has_access(self.access_level)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login_page', next=request.url))


class EventView(AuthorizedView):
    access_level = 'event_admin'
    column_editable_list = ['name', 'registration_open']
    form_widget_args = {
        'description': {
            'rows': 4,
            'style': 'width: 100%;',
        },
        'registration_schema': {
            'rows': 16,
            'style': 'width: 100%; font-family: monospace;',
        }
    }
    form_overrides = {
        'registration_schema': PrettyJSONField
    }


class RoleView(AuthorizedView):
    column_display_pk = True
    column_list = ['id', 'access_levels']
    form_columns = ['id', 'access_levels']
    access_level = 'role_admin'


class AccessLevelView(AuthorizedView):
    column_display_pk = True
    form_columns = ['id']
    access_level = 'access_level_admin'
