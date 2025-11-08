"""Plugin hooks for contrib_auth plugin."""

from djadmin.plugins import hookimpl


@hookimpl
def djadmin_get_action_view_mixins(action):
    """
    Register view mixins for contrib_auth actions.

    The PasswordChangeViewMixin handles the special case of using a plain
    Form (not ModelForm) with UpdateView. It converts the 'instance' kwarg
    to 'user' kwarg and provides get_form_class() and get_fields() methods.

    Returns:
        Dict mapping action classes to mixin lists
    """
    from .actions import ChangePasswordAction, PasswordChangeViewMixin

    return {
        ChangePasswordAction: [PasswordChangeViewMixin],
    }
