"""
Dashboard action for project and app-level views.

This is a unified implementation that handles both project dashboard (all apps)
and app dashboard (single app) based on the presence of app_label in kwargs.

Implementation for Milestone 5A.
"""

from djadmin.actions.base import BaseAction
from djadmin.actions.view_mixins import TemplateViewActionMixin


class DashboardAction(TemplateViewActionMixin, BaseAction):
    """
    Unified dashboard action showing ModelAdmins for an app or all apps.

    If app_label is provided (via URL kwargs), shows only that app.
    If app_label is None, shows all apps (project dashboard).

    This is a site-level action that doesn't operate on a specific model,
    so model and model_admin are None.
    """

    label = 'Dashboard'
    url_name = 'index'

    def __init__(self, admin_site):
        """Initialize without model/model_admin since this is a site-level view."""
        # Dashboard doesn't operate on a specific model
        super().__init__(model=None, model_admin=None, admin_site=admin_site)

    def get_template_names(self):
        """
        Return template based on whether we're showing single app or all apps.

        This method is called by Django CBV and has access to self.kwargs on the view.
        """
        # When bound to view, self.kwargs will be available
        app_label = self.kwargs.get('app_label') if hasattr(self, 'kwargs') else None

        if app_label:
            return ['djadmin/app_dashboard.html']
        else:
            return ['djadmin/project_dashboard.html']

    def get_context_data(self, **kwargs):
        """Provide dashboard data."""
        context = super(type(self), self).get_context_data(**kwargs)

        # Check if filtering by app (from URL kwargs)
        app_label = kwargs.get('app_label')

        if app_label:
            # Single app dashboard
            context.update(self._get_app_context(app_label, request=self.request))
        else:
            # Project dashboard (all apps)
            context.update(self._get_all_apps_context(request=self.request))

        return context

    def _get_app_context(self, app_label: str, request) -> dict:
        """Get context for single app dashboard."""
        from django.apps import apps
        from django.core.exceptions import PermissionDenied
        from django.http import Http404

        # Check if app exists in Django
        try:
            app_config = apps.get_app_config(app_label)
            app_verbose_name = app_config.verbose_name
        except LookupError as e:
            # Get list of valid apps that have registered models
            valid_apps = sorted({model._meta.app_label for model in self.admin_site._registry.keys()})
            raise Http404(
                f"App '{app_label}' not found. "
                f"Valid apps with registered models: {', '.join(valid_apps) if valid_apps else 'none'}"
            ) from e

        # Build list of ModelAdmins with their actions (filtered by permissions)
        model_admin_list = self._get_model_admins_for_app(app_label, request=request)

        # If user has no access to any models in this app, deny permission
        if not model_admin_list:
            raise PermissionDenied(f"You do not have permission to access any models in the '{app_verbose_name}' app.")

        return {
            'app_label': app_label,
            'app_verbose_name': app_verbose_name,
            'model_admin_list': model_admin_list,
        }

    def _get_all_apps_context(self, request) -> dict:
        """Get context for project dashboard (all apps)."""
        from django.apps import apps as django_apps

        # Group ModelAdmins by app
        apps_dict = {}
        for model, model_admins in self.admin_site._registry.items():
            app_label = model._meta.app_label

            if app_label not in apps_dict:
                try:
                    app_config = django_apps.get_app_config(app_label)
                    verbose_name = app_config.verbose_name
                except Exception:
                    verbose_name = app_label.title()

                apps_dict[app_label] = {
                    'name': app_label,
                    'verbose_name': verbose_name,
                    'url': self.admin_site.reverse(f'{app_label}_app_index', kwargs={'app_label': app_label}),
                    'model_admins': [],
                }

            # Get ModelAdmins for this app (filtered by permissions)
            model_admins_data = self._get_model_admins_for_app(
                app_label, model=model, model_admins=model_admins, request=request
            )
            apps_dict[app_label]['model_admins'].extend(model_admins_data)

        # Filter out apps with no accessible models
        app_list = [app for app in apps_dict.values() if app['model_admins']]

        # Sort apps and their ModelAdmins
        app_list.sort(key=lambda x: x['name'])
        for app in app_list:
            app['model_admins'].sort(key=lambda x: x['display_name'])

        return {
            'app_list': app_list,
        }

    def _get_model_admins_for_app(self, app_label: str, model=None, model_admins=None, request=None) -> list:
        """
        Get list of ModelAdmins with their actions for an app.

        Args:
            app_label: App label to filter by
            model: Optional specific model (for project dashboard)
            model_admins: Optional specific model_admins (for project dashboard)
            request: Optional request object for permission filtering

        Returns:
            List of dicts with ModelAdmin data and actions (filtered by permissions)
        """
        result = []

        # If model/model_admins provided, use those
        # Otherwise, loop through all models in app
        if model and model_admins:
            items_to_process = [(model, model_admins)]
        else:
            items_to_process = [
                (m, mas) for m, mas in self.admin_site._registry.items() if m._meta.app_label == app_label
            ]

        for model, model_admins in items_to_process:
            # Each ModelAdmin is listed separately
            for idx, model_admin in enumerate(model_admins):
                # Filter general actions by permissions if request provided
                if request:
                    general_actions_filtered = model_admin.filter_actions(model_admin.general_actions, request)
                else:
                    general_actions_filtered = model_admin.general_actions

                # Skip ModelAdmins with no accessible actions
                if not general_actions_filtered:
                    continue

                # Get action data for display
                general_actions = self._get_action_data(
                    model, model_admin, general_actions_filtered, idx if len(model_admins) > 1 else None
                )

                # Create display name
                if len(model_admins) > 1:
                    display_name = f'{model._meta.verbose_name_plural} ({model_admin.__class__.__name__})'
                else:
                    display_name = model._meta.verbose_name_plural

                result.append(
                    {
                        'model': model,
                        'model_admin': model_admin,
                        'display_name': display_name,
                        'general_actions': general_actions,
                    }
                )

        return result

    def _get_action_data(self, model, model_admin, actions: list, admin_idx=None) -> list:
        """
        Get action data (label, URL) for a list of action instances.

        Uses Django's reverse() to generate URLs properly.

        Args:
            model: Model class
            model_admin: ModelAdmin instance
            actions: List of action instances (already instantiated by ModelAdmin)
            admin_idx: Index if multiple ModelAdmins (for URL generation)

        Returns:
            List of dicts with action data
        """
        action_list = []

        for action in actions:
            # Use the action's url_name property with reverse()
            try:
                url = self.admin_site.reverse(action.url_name)
            except Exception:
                # If reverse fails, skip this action
                continue

            action_list.append(
                {
                    'label': action.label,
                    'url': url,
                    'css_class': getattr(action, 'css_class', ''),
                    'icon': getattr(action, 'icon', None),
                }
            )

        return action_list
