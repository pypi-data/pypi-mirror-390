"""AppConfig for permissions plugin"""

from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    """Configuration for permissions plugin"""

    name = 'djadmin.plugins.permissions'
    label = 'djadmin_permissions'
    verbose_name = 'Django Admin Deux - Permissions'
    default_auto_field = 'django.db.models.BigAutoField'
