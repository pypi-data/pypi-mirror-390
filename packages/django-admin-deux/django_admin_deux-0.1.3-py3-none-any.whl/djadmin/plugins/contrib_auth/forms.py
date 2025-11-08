"""Forms for User and Group admin."""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    Form for creating new users. Includes password fields.

    This form is compatible with both standard Django forms and djadmin-formset plugin.

    The password fields (password1, password2) are NOT model fields, so they're
    defined directly on the form and handled separately in save().
    """

    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Your password must contain at least 8 characters and cannot be entirely numeric.'),
        required=True,
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
        required=True,
    )

    class Meta:
        model = User
        # Include USERNAME_FIELD and REQUIRED_FIELDS dynamically
        # For standard User model: USERNAME_FIELD='username', REQUIRED_FIELDS=['email']
        # PASSWORD FIELDS ARE NOT INCLUDED HERE - they're defined above as form fields
        fields = [User.USERNAME_FIELD] + User.REQUIRED_FIELDS
        field_classes = {User.USERNAME_FIELD: forms.CharField}

    def clean_password2(self):
        """Validate that the two password fields match."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        """
        Validate password after cleaning.

        This runs Django's built-in password validators.
        """
        super()._post_clean()
        # Get password from cleaned_data (not yet popped)
        password = self.cleaned_data.get('password2')
        if password:
            try:
                from django.contrib.auth.password_validation import validate_password

                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        """Save user with hashed password."""
        user = super().save(commit=False)
        # Get password from cleaned_data
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Form for updating users.

    The password field is excluded - use the "Change Password" action instead.
    Note: We use fields='__all__' but password is a non-editable field, so it
    won't be included in the form anyway.
    """

    class Meta:
        model = User
        # Use all fields - password is excluded automatically (non-editable)
        fields = '__all__'  # noqa: DJ007


class UserPasswordChangeForm(forms.Form):
    """
    Form for changing user passwords.

    This form is used by the ChangePasswordAction and provides password1/password2
    fields for entering and confirming the new password. It's compatible with both
    standard Django forms and djadmin-formset plugin.

    Note: This is a plain Form (not ModelForm) since it only contains form fields
    (password1, password2) and no model fields.
    """

    password1 = forms.CharField(
        label=_('New password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_('Your password must contain at least 8 characters and cannot be entirely numeric.'),
        required=True,
    )
    password2 = forms.CharField(
        label=_('New password confirmation'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        """Initialize form with user instance."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        """Validate that the two password fields match."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        """
        Validate password after cleaning.

        This runs Django's built-in password validators.
        """
        super()._post_clean()
        # Get password from cleaned_data (not yet popped)
        password = self.cleaned_data.get('password2')
        if password and self.user:
            try:
                from django.contrib.auth.password_validation import validate_password

                validate_password(password, self.user)
            except ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        """Save user with hashed password."""
        if not self.user:
            raise ValueError('User instance is required to save password')

        # Get password from cleaned_data
        password = self.cleaned_data.get('password1')
        if password:
            self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
