from importlib import import_module

from django.apps import AppConfig, apps
from django.core.exceptions import ImproperlyConfigured


def djadmin_apps():
    """
    Get all required INSTALLED_APPS from plugins.

    Discovers plugins from two sources:
    1. Built-in plugins (djadmin.plugins.core, djadmin.plugins.theme)
    2. Third-party plugins via entrypoints (pyproject.toml [project.entry-points.djadmin])

    Collects apps from djadmin_get_required_apps() hooks and resolves
    ordering using First/Before/After/Position modifiers.

    Returns:
        list: App names in correct order, with duplicates removed.

    Raises:
        ImproperlyConfigured: If circular dependencies detected or positioning fails.

    Example:
        # settings.py
        from djadmin import djadmin_apps

        INSTALLED_APPS = [
            'django.contrib.admin',
            # ... other apps
        ] + djadmin_apps()

    Third-party plugins should declare themselves via entrypoints:
        # pyproject.toml
        [project.entry-points.djadmin]
        my_plugin = "my_plugin.djadmin_hooks"
    """
    from djadmin.plugins import pm

    # Register built-in plugins from djadmin/plugins/ folder
    from djadmin.plugins.core import djadmin_hooks as core_hooks
    from djadmin.plugins.modifiers import After, Before, First, Position
    from djadmin.plugins.theme import djadmin_hooks as theme_hooks

    if not pm.is_registered(core_hooks):
        pm.register(core_hooks)
    if not pm.is_registered(theme_hooks):
        pm.register(theme_hooks)

    # Discover third-party plugins via entrypoints (only once)
    # Plugins declare themselves in pyproject.toml: [project.entry-points.djadmin]
    # Load entrypoints manually to skip already-registered plugins
    if not hasattr(djadmin_apps, '_entrypoints_loaded'):
        from importlib.metadata import entry_points

        for ep in entry_points(group='djadmin'):
            plugin = ep.load()
            # Skip if already registered (e.g., via DjAdminConfig.ready())
            if not pm.is_registered(plugin):
                pm.register(plugin, name=ep.name)

        djadmin_apps._entrypoints_loaded = True

    # Collect apps from all plugins, categorized by type
    first = []
    before = []
    after = []
    default = []
    position_items = []

    # Always include djadmin core in default
    default.append('djadmin')

    # Get apps from plugin hooks
    hook_results = pm.hook.djadmin_get_required_apps()
    for result in hook_results:
        if not result:
            continue

        for item in result:
            if isinstance(item, First):
                first.append(item.app)
            elif isinstance(item, Before):
                before.append(item.app)
            elif isinstance(item, After):
                after.append(item.app)
            elif isinstance(item, Position):
                position_items.append(item)
            elif isinstance(item, str):
                default.append(item)
            else:
                raise ImproperlyConfigured(
                    f'Invalid item in djadmin_get_required_apps() hook: {item}\n'
                    f'Expected: str, First, Before, After, or Position'
                )

    # Combine: first + before + default + after
    combined = first + before + default + after

    # Handle Position items (relative positioning)
    for item in position_items:
        if item.before:
            try:
                idx = combined.index(item.before)
                combined.insert(idx, item.app)
            except ValueError as e:
                raise ImproperlyConfigured(
                    f'Cannot position {item.app} before {item.before}: ' f'{item.before} not found in apps list'
                ) from e
        elif item.after:
            try:
                idx = combined.index(item.after)
                combined.insert(idx + 1, item.app)
            except ValueError as e:
                raise ImproperlyConfigured(
                    f'Cannot position {item.app} after {item.after}: ' f'{item.after} not found in apps list'
                ) from e

    # Remove duplicates while preserving order
    seen = set()
    unique_apps = []
    for app in combined:
        if app not in seen:
            seen.add(app)
            unique_apps.append(app)

    return unique_apps


class DjAdminConfig(AppConfig):
    name = 'djadmin'
    verbose_name = 'Django Admin Deux'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """Initialize plugin system and validate ModelAdmin classes"""
        from djadmin.plugins import pm

        # Register built-in plugins (always enabled)
        from djadmin.plugins.core import djadmin_hooks as core_hooks
        from djadmin.plugins.permissions import djadmin_hooks as permissions_hooks

        if not pm.is_registered(core_hooks):
            pm.register(core_hooks)
        if not pm.is_registered(permissions_hooks):
            pm.register(permissions_hooks)

        # Discover plugins and djadmin modules from INSTALLED_APPS
        for app_config in apps.get_app_configs():
            # Skip django's own apps
            if app_config.name.startswith('django.'):
                continue

            # Try to import app's djadmin_hooks module (plugins)
            try:
                hooks_module = import_module(f'{app_config.name}.djadmin_hooks')
                if not pm.is_registered(hooks_module):
                    pm.register(hooks_module)
            except ImportError:
                # No djadmin_hooks module in this app
                pass

            # Try to import app's djadmin module (model registrations)
            try:
                import_module(f'{app_config.name}.djadmin')
            except ImportError:
                # No djadmin module in this app
                # TODO: Distinguish between "file doesn't exist" vs "file exists but has import error"
                # Should raise exception for import errors to help developers debug
                pass

        # Check if any plugin provides 'theme' feature
        all_features = self._get_all_provided_features()

        if 'theme' not in all_features:
            # Auto-enable default theme
            from djadmin.plugins.theme import djadmin_hooks as theme_hooks

            if not pm.is_registered(theme_hooks):
                pm.register(theme_hooks)

        # Validate ModelAdmin classes
        self._validate_model_admins()

    def _get_all_provided_features(self):
        """Get all features provided by registered plugins"""
        from djadmin.plugins import pm

        all_features = set()
        # Call the hook and collect results
        results = pm.hook.djadmin_provides_features()
        for feature_list in results:
            if feature_list:
                all_features.update(feature_list)

        return all_features

    def _validate_model_admins(self):
        """Validate that all ModelAdmin requested features are provided by plugins"""
        from django.core.exceptions import ImproperlyConfigured

        from djadmin.sites import site

        # Get all provided features
        all_features = self._get_all_provided_features()

        # Validate each registered ModelAdmin
        for model, model_admin_list in site._registry.items():
            for model_admin in model_admin_list:
                requested = model_admin.requested_features
                missing = requested - all_features

                if missing:
                    raise ImproperlyConfigured(
                        f'ModelAdmin {model_admin.__class__.__name__} for model '
                        f'{model._meta.label} requests features {missing} '
                        f'but no registered plugin provides them.\n'
                        f'Requested: {requested}\n'
                        f'Available: {all_features}\n'
                        f'Install required plugins or remove the configuration.'
                    )
