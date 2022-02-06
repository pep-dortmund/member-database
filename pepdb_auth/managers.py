from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _



class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError(_('email required'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password is not None:
            user.set_password(password)

        user.save()
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        extra_fields['is_active'] = True

        return self.create_user(email=email, name=name, password=password, **extra_fields)
