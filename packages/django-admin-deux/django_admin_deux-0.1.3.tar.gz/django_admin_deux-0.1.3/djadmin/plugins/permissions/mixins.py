# djadmin/plugins/permissions/mixins.py

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class PermissionMixin(UserPassesTestMixin):
    """
    Mixin that provides permission checking for views.

    Provides:
    - test_func() for UserPassesTestMixin view-level permission checks
    - get_object() override for object-level permission checks
    """

    def test_func(self):
        """
        Permission check method for UserPassesTestMixin.

        This method is called by UserPassesTestMixin to check if the user
        has permission to access the view.

        Returns:
            bool: True if user has permission, False otherwise
        """
        # Get permission from action or model_admin
        perm = self._get_permission_class()

        if perm is None:
            # None means no permission enforcement (allow all access)
            # This happens when:
            # 1. Explicitly set to None on ModelAdmin or Action
            # 2. No model_admin exists (site-level views like DashboardAction)
            return True

        # Execute permission with view (self is the view)
        return perm(self)

    def get_object(self, queryset=None):
        """Override to check object permissions after fetching."""
        obj = super().get_object(queryset)

        # Get permission class from action or model_admin
        permission_class = self._get_permission_class()

        if permission_class is not None:
            # Check object permission
            if not permission_class.has_object_permission(self, obj):
                raise PermissionDenied(f'You do not have permission to access this {obj._meta.verbose_name}.')

        return obj

    def _get_permission_class(self):
        """
        Get the permission class to use for checks.

        Returns the actual Permission instance from action or model_admin.
        """
        # Get permission from action (highest priority)
        perm = getattr(self.action, 'permission_class', None)

        # Fall back to ModelAdmin
        if perm is None and hasattr(self, 'model_admin'):
            perm = getattr(self.model_admin, 'permission_class', None)

        return perm
