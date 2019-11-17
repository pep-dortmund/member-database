from flask import Blueprint, redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class ModelView(ModelView):
    '''ModelView that honors our access rights'''

    def __init__(self, *args, access_required=None, **kwargs):
        self.access_required = access_required
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if self.access_required is None:
            return current_user.is_authenticated
        return current_user.has_access(self.access_required)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.full_path))


class Blueprint(Blueprint):
    ''' A blueprint that supports adding admin views from flask_admin
    Adapted from http://blog.sadafnoor.me/blog/how-to-add-flask-admin-to-a-blueprint/
    '''

    def __init__(self, name, *args, **kwargs):
        self.views = []
        self.admin = Admin(name=name, template_mode='bootstrap3')
        return super().__init__(name, *args, **kwargs)

    def add_view(self, view):
        self.views.append(view)

    def register(self, app, options, first_registration=False):
        self.admin.init_app(app)

        for v in self.views:
            self.admin.add_view(v)

        return super().register(app, options, first_registration)
