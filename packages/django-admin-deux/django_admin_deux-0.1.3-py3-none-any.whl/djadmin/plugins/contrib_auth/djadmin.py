"""
Auto-register User and Group models with their admin classes.

This module is auto-discovered by djadmin when the plugin is in INSTALLED_APPS.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import User as ContribAuthUser
from django.utils.translation import gettext_lazy as _

from djadmin import Field, Fieldset, Layout, ModelAdmin, register

from .actions import ChangePasswordAction
from .forms import UserChangeForm, UserCreationForm

User = get_user_model()


@register(Group)
class GroupAdmin(ModelAdmin):
    """
    Admin for Django's Group model.

    Provides basic CRUD operations with search and M2M permissions management.
    """

    search_fields = ['name']
    ordering = ['name']
    list_display = ['name']

    layout = Layout(
        Field('name'),
        Field('permissions'),  # M2M field, uses standard SelectMultiple
    )


@register(User)
class UserAdmin(ModelAdmin):
    """
    Admin for Django's User model (or custom user model).

    Features:
    - Different forms for create vs update (passwords vs read-only hash)
    - Different layouts for create vs update
    - List display with username, email, name, staff status
    - List filters for staff, superuser, active, groups
    - Search across username, email, first/last name
    - Password change action with custom URL
    """

    # Different forms for create vs update
    create_form_class = UserCreationForm
    update_form_class = UserChangeForm

    # List view configuration
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']

    def __init__(self, model, admin_site):
        """Initialize UserAdmin and add password change action to record actions."""
        super().__init__(model, admin_site)
        # Add password change action to the existing record actions (don't replace them)
        self.record_actions.append(ChangePasswordAction(model, self, admin_site))

        self.create_layout = Layout(
            Fieldset(
                _('User Information'),
                *[Field(x) for x in [model.USERNAME_FIELD] + model.REQUIRED_FIELDS],
            ),
            Fieldset(
                _('Password'),
                Field('password1'),
                Field('password2'),
            ),
        )

        if issubclass(User, ContribAuthUser):
            # Update layout - full user details
            self.update_layout = Layout(
                Fieldset(
                    None,
                    Field('username'),
                ),
                Fieldset(
                    _('Personal info'),
                    Field('first_name'),
                    Field('last_name'),
                    Field('email'),
                ),
                Fieldset(
                    _('Permissions'),
                    Field('is_active'),
                    Field('is_staff'),
                    Field('is_superuser'),
                    Field('groups'),  # M2M, standard SelectMultiple
                    Field('user_permissions'),  # M2M, standard SelectMultiple
                ),
                Fieldset(
                    _('Important dates'),
                    Field('last_login'),
                    Field('date_joined'),
                ),
            )
