"""Django app configuration for contrib_auth plugin."""

from django.apps import AppConfig


class ContribAuthConfig(AppConfig):
    """App config for contrib_auth plugin."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djadmin.plugins.contrib_auth'
    verbose_name = 'Django Admin Deux - Auth Plugin'
