from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(BaseUserAdmin):

    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = ('email', 'name', 'is_staff', 'is_active',)
    list_filter = ('email', 'name', 'is_staff', 'is_active',)

    fieldsets = (
        (None, {'fields': ('email', 'password', 'name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('email', 'name')
    ordering = ('email', 'name')


admin.site.register(User, UserAdmin)
