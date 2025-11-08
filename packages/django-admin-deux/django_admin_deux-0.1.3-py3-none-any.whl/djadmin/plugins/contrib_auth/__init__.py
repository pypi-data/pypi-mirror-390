"""
contrib_auth plugin for django-admin-deux.

Provides pre-built UserAdmin and GroupAdmin classes for Django's authentication models.

Note: Models are auto-registered via djadmin.py when this plugin is in INSTALLED_APPS.
To manually import admin classes: from djadmin.plugins.contrib_auth.djadmin import UserAdmin, GroupAdmin
"""

# Django app configuration
default_app_config = 'djadmin.plugins.contrib_auth.apps.ContribAuthConfig'
