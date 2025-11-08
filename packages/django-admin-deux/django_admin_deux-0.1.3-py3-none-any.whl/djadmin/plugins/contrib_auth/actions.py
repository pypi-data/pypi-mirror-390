"""Custom actions for User/Group admin."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from djadmin.actions.base import BaseAction, RecordActionMixin, WithSuccessUrlActionMixin
from djadmin.actions.view_mixins import UpdateViewActionMixin
from djadmin.layout import Field, Fieldset, Layout

from .forms import UserPasswordChangeForm


class PasswordChangeViewMixin:
    """
    Mixin for password change views using non-ModelForm forms.

    This mixin handles the differences between ModelForm-based UpdateViews
    and plain Form-based password change forms:
    - Converts 'instance' kwarg to 'user' kwarg for the form
    - Provides get_form_class() that returns UserPasswordChangeForm
    - Provides get_fields() that returns empty list
    """

    def get_form_class(self):
        """Return the UserPasswordChangeForm."""
        return UserPasswordChangeForm

    def get_fields(self):
        """Return empty list since form has no model fields."""
        return []

    def get_layout(self):
        return None

    def get_form_kwargs(self):
        """
        Customize form kwargs to pass user instead of instance.

        UpdateView normally passes 'instance' for ModelForms, but our
        UserPasswordChangeForm expects 'user' kwarg instead.
        """
        kwargs = super().get_form_kwargs()

        # Remove 'instance' that UpdateView adds (for ModelForms)
        user = kwargs.pop('instance', None)

        # Add 'user' kwarg that our form expects
        if user:
            kwargs['user'] = user

        return kwargs


class ChangePasswordAction(WithSuccessUrlActionMixin, RecordActionMixin, UpdateViewActionMixin, BaseAction):
    """
    Custom action to change user password.

    Adds a /password/ URL to the user detail view.
    Uses our custom UserPasswordChangeForm with password1/password2 fields.

    The PasswordChangeViewMixin (registered via plugin hook) handles:
    - Converting UpdateView's 'instance' kwarg to 'user' kwarg for the form
    - Providing get_form_class() and get_fields() methods

    Note: Layout is needed here because password1/password2 are form-only fields
    (not model fields). The layout explicitly tells the factory which fields to render.
    """

    label = _('Change password')
    icon = 'lock'

    # Define layout explicitly to specify which form fields to render
    # These are form-only fields, not model fields
    layout = Layout(
        Fieldset(
            _('Change Password'),
            Field('password1'),
            Field('password2'),
        )
    )

    def get_template_names(self):
        """
        Get template name for password change form.

        Returns:
            Template path string
        """
        return [
            'djadmin/actions/changepassword.html',
            'djadmin/actions/edit.html',  # Use standard edit template
        ]

    def get_url_pattern(self):
        """
        Custom URL pattern: /auth/user/123/password/

        Returns:
            URL pattern string
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/<int:pk>/password/'

    @property
    def url_name(self):
        """
        URL name: djadmin:auth_user_password

        Returns:
            URL name string
        """
        opts = self.model._meta
        return f'{opts.app_label}_{opts.model_name}_password'

    def form_valid(self, form):
        """
        Save the new password and redirect.

        Args:
            form: Valid form instance

        Returns:
            HttpResponse redirect
        """
        form.save()
        messages.success(self.request, _('Password changed successfully.'))
        # Redirect to user detail view
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Redirect back to user list view.

        Returns:
            URL string
        """
        opts = self.model._meta
        return self.admin_site.reverse(f'{opts.app_label}_{opts.model_name}_list')
