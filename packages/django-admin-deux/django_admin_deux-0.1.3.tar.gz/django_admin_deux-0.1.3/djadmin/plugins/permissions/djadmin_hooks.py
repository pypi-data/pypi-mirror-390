"""Plugin hooks for permissions system"""

from djadmin.plugins import hookimpl


@hookimpl
def djadmin_provides_features():
    """Advertise that this plugin provides 'permissions' feature."""
    return ['permissions']


@hookimpl
def djadmin_get_action_view_mixins(action):
    """
    Add UserPassesTestMixin and PermissionMixin to ALL action views.

    Uses isinstance() matching with BaseAction to apply to everything.

    Args:
        action: The action instance

    Returns:
        Dict mapping action types to mixin lists
    """

    from djadmin.actions import BaseAction
    from djadmin.plugins.permissions.mixins import PermissionMixin

    return {BaseAction: [PermissionMixin]}
