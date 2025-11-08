"""
django-admin-deux: A modern, extensible Django admin interface
"""

__version__ = '0.1.3'

# Expose public API
from djadmin.apps import djadmin_apps
from djadmin.dataclasses import Column, ColumnHeaderIcon, CSSAsset, Filter, JSAsset, Order, SidebarWidget
from djadmin.decorators import register
from djadmin.inlines import InlineModelAdmin, StackedInline, TabularInline
from djadmin.layout import Collection, Field, Fieldset, Layout, Row
from djadmin.options import ModelAdmin
from djadmin.plugins.modifiers import After, Before, First, Position, Remove, Replace
from djadmin.sites import AdminSite, site

__all__ = [
    'AdminSite',
    'site',
    'ModelAdmin',
    'Column',
    'ColumnHeaderIcon',
    'Filter',
    'Order',
    'SidebarWidget',
    'JSAsset',
    'CSSAsset',
    'register',
    # Layout API
    'Layout',
    'Field',
    'Fieldset',
    'Row',
    'Collection',
    # Inline compatibility (deprecated)
    'InlineModelAdmin',
    'TabularInline',
    'StackedInline',
    # Modifiers
    'Remove',
    'Replace',
    'First',
    'Before',
    'After',
    'Position',
    # INSTALLED_APPS management
    'djadmin_apps',
]
