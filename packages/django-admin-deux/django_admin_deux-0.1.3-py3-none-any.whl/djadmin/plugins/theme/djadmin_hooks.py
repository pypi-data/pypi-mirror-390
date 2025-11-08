from djadmin import CSSAsset
from djadmin.actions.base import BaseAction
from djadmin.plugins import hookimpl
from djadmin.plugins.modifiers import First


@hookimpl
def djadmin_provides_features():
    return ['theme']


@hookimpl
def djadmin_get_action_view_assets(action):
    """
    Provide theme CSS and JS for all action views.

    Uses registry pattern - returns dict mapping action classes to assets.
    BaseAction means these assets apply to ALL actions.

    Note: Our theme.css includes custom styling for django-formset
    FormCollections to match the djadmin theme.
    """
    return {
        BaseAction: {
            'css': [
                CSSAsset(href='djadmin/theme/css/theme.css'),
            ],
            'js': ['djadmin/theme/js/admin.js'],
        }
    }


@hookimpl
def djadmin_get_required_apps():
    """
    Theme plugin loads first for template precedence.

    Note: This hook only runs if the default theme plugin is registered,
    which happens only when no other plugin provides the 'theme' feature.
    See djadmin.apps.DjAdminConfig.ready() for auto-registration logic.
    """
    return [
        First('djadmin.plugins.theme'),
    ]
