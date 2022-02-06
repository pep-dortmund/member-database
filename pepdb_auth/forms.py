from django.contrib.auth import forms

from .models import User

__all__ = [
    'UserCreationForm',
    'UserChangeForm',
]


class UserCreationForm(forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    class Meta:
        model = User
        fields = ('email', 'name')


class UserChangeForm(forms.UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'name')

