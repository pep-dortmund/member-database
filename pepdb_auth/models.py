from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    # we remove these fields since we are using email as username and a common
    # name field
    username = None
    first_name = None
    last_name = None

    name = models.CharField(_("name"), max_length=100)
    email = models.EmailField(_("email address"), unique=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __repr__(self):
        return f"User(email={self.email})"
