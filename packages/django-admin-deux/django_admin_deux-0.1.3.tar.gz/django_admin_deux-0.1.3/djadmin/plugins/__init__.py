"""Plugin system for django-admin-deux using djp"""

import sys

import djp
import pluggy

from djadmin.plugins.modifiers import After, Before, First, Position, Remove, Replace

# Create plugin manager
pm = djp.PluginManager('djadmin')

# Define hook specifications using pluggy
hookspec = pluggy.HookspecMarker('djadmin')


@hookspec
def djadmin_provides_features():
    """Return list of feature names this plugin provides"""
    pass


@hookspec
def djadmin_get_form_features(action, model_admin):
    """
    Advertise features required by a form.

    Called by CreateAction and UpdateAction to determine what features
    the form needs. Plugins check these features and decide whether to
    hook in.

    Args:
        action: The action instance (AddAction/EditRecordAction)
        model_admin: The ModelAdmin instance

    Returns:
        Set of feature names (strings)
    """
    pass


# Action hooks
@hookspec
def djadmin_get_default_general_actions():
    """Return list of default general actions (main entry points like ListView, Add)"""
    pass


@hookspec
def djadmin_get_default_bulk_actions():
    """Return list of default bulk actions"""
    pass


@hookspec
def djadmin_get_default_record_actions():
    """Return list of default record actions"""
    pass


# Action view hooks - registry-based
@hookspec
def djadmin_get_action_view_mixins(action):
    """
    Return dictionary mapping action classes to mixin lists.

    Factory will check isinstance(action, key) for each key.
    This allows plugins to register mixins for specific action classes
    or base classes (like view-type mixins).

    Args:
        action: Action instance (for context, e.g., access to model_admin)

    Returns:
        Dict mapping action classes to list of mixin classes

    Example:
        @hookimpl
        def djadmin_get_action_view_mixins(action):
            from djadmin.actions.list_view import ListViewAction
            from djadmin.actions.view_mixins import FormViewActionMixin

            return {
                ListViewAction: [PaginationMixin, SortingMixin],
                FormViewActionMixin: [FormProcessingMixin],
            }
    """
    pass


@hookspec
def djadmin_get_action_view_base_class(action):
    """
    Return dictionary mapping action classes to base class overrides.

    Factory will check isinstance(action, key) for each key.
    Allows plugins to override the base view class for specific actions.

    Args:
        action: Action instance

    Returns:
        Dict mapping action classes to view base classes

    Example:
        return {
            CustomListAction: CustomListView,
        }
    """
    pass


@hookspec
def djadmin_get_action_view_assets(action):
    """
    Return dictionary mapping action classes to asset dicts.

    Factory will check isinstance(action, key) for each key.

    Assets can be specified as either:
    - Plain strings (backward compatible): 'path/to/file.css'
    - Asset objects (for advanced features): JSAsset(src='file.js', module=True)

    The system automatically normalizes all assets to CSSAsset/JSAsset objects.

    Args:
        action: Action instance

    Returns:
        Dict mapping action classes to {'css': [...], 'js': [...]}

    Examples:
        # String assets (backward compatible)
        return {
            ListViewAction: {
                'css': ['admin/list.css'],
                'js': ['admin/list.js'],
            },
        }

        # Asset objects with attributes
        from djadmin import JSAsset, CSSAsset
        return {
            FormViewActionMixin: {
                'js': [
                    JSAsset(src='formset/django-formset.js', module=True, blocking=True),
                    JSAsset(src='theme/admin.js', defer=True),
                ],
                'css': [CSSAsset(href='formset/custom.css', media='print')],
            },
        }

        # Mixed (both types work together)
        return {
            BaseAction: {
                'css': ['theme.css', CSSAsset(href='print.css', media='print')],
                'js': ['legacy.js', JSAsset(src='module.js', module=True)],
            },
        }
    """
    pass


@hookspec
def djadmin_get_action_view_attributes(action):
    """
    Return dictionary mapping action classes to attribute dicts.

    Factory will check isinstance(action, key) for each key.
    This is the main mechanism for plugins to add view attributes
    based on action type.

    Args:
        action: Action instance (has access to model, admin_admin, admin_site)

    Returns:
        Dict mapping action classes to attribute dicts

    Example:
        @hookimpl
        def djadmin_get_action_view_attributes(action):
            from djadmin.actions.view_mixins import ListViewActionMixin

            return {
                ListViewActionMixin: {
                    'paginate_by': action.model_admin.paginate_by,
                    'ordering': action.model_admin.ordering,
                },
            }
    """
    pass


@hookspec
def djadmin_get_action_view_attribute_bindings(action):
    """
    Return dictionary mapping action classes to lists of attribute names to bind.

    These attributes will be copied directly from the action instance to the view class.
    This is useful for methods, properties, or any attribute that should be delegated
    to the action.

    Factory will check isinstance(action, key) for each key.

    Args:
        action: Action instance

    Returns:
        Dict mapping action classes to list of attribute names (strings)

    Example:
        @hookimpl
        def djadmin_get_action_view_attribute_bindings(action):
            from djadmin.actions.base import BaseAction
            from djadmin.actions.view_mixins import ListViewActionMixin

            return {
                BaseAction: ['get_template_names'],
                ListViewActionMixin: ['get_queryset'],
            }
    """
    pass


# Action registration hooks
@hookspec
def djadmin_register_actions():
    """
    Allow plugins to register custom action classes.

    Returns:
        Dict mapping action identifiers to action classes

    Example:
        return {
            'export_pdf': ExportPDFAction,
            'send_email': SendEmailAction,
        }
    """
    pass


# Query and context hooks
@hookspec
def djadmin_modify_queryset(queryset, request, view):
    """Modify queryset before rendering ListView"""
    pass


@hookspec
def djadmin_add_context_data(context, request, view):
    """Add extra context data to views"""
    pass


# Sidebar hooks
@hookspec
def djadmin_get_sidebar_widgets(action):
    """
    Return dictionary mapping action classes to sidebar widget lists.

    Sidebar widgets allow plugins to add content to a dedicated sidebar area
    in action views (e.g., filters, quick actions, help text).

    Factory will check isinstance(action, key) for each key and collect
    all matching widgets, sorted by order.

    Args:
        action: Action instance (has access to model, model_admin, admin_site)

    Returns:
        Dict mapping action classes to list of SidebarWidget instances

    Example:
        @hookimpl
        def djadmin_get_sidebar_widgets(action):
            from djadmin.actions.list_view import ListViewAction
            from djadmin_filters.widgets import FilterSidebarWidget

            return {
                ListViewAction: [
                    FilterSidebarWidget(order=10),
                ],
            }
    """
    pass


# Column header hooks
@hookspec
def djadmin_get_column_header_icons(action):
    """
    Return dictionary mapping action classes to column header icon lists.

    Column header icons allow plugins to add interactive elements to table
    column headers (e.g., sort indicators, help text, filters). Icons are
    evaluated per-column and can be conditional.

    Factory will check isinstance(action, key) for each key and collect
    all matching icons, sorted by order. Icons are passed to the template
    context where they can be rendered for each column.

    Args:
        action: Action instance (has access to model, model_admin, admin_site)

    Returns:
        Dict mapping action classes to list of ColumnHeaderIcon instances

    Example:
        @hookimpl
        def djadmin_get_column_header_icons(action):
            from djadmin import ColumnHeaderIcon
            from djadmin.actions.list_view import ListViewAction

            def get_sort_url(column, view, request):
                current_ordering = request.GET.get('ordering', '')
                field_name = column.field_name
                if current_ordering == field_name:
                    return f'?ordering=-{field_name}'
                return f'?ordering={field_name}'

            def get_sort_icon(column, view, request):
                current_ordering = request.GET.get('ordering', '')
                field_name = column.field_name
                if current_ordering == field_name:
                    return 'djadmin/icons/sort-up.html'
                elif current_ordering == f'-{field_name}':
                    return 'djadmin/icons/sort-down.html'
                return 'djadmin/icons/sort.html'

            return {
                ListViewAction: [
                    ColumnHeaderIcon(
                        icon_template=get_sort_icon,  # Can be callable
                        url=get_sort_url,  # Can be callable
                        title='Sort by this column',
                        condition=lambda col, view, req: bool(col.order),
                        order=10,
                    ),
                ],
            }
    """
    pass


# Testing hooks
@hookspec
def djadmin_get_test_methods():
    """
    Provide custom test methods for action testing.

    Plugins can use this to provide specialized test methods for actions
    they modify. For example, djadmin-formset needs different POST data
    formatting than standard Django forms.

    Test methods can be:
    - Callables: Direct test method implementations
    - Remove(): Modifier to remove a test method from a base class
    - Replace(): Modifier to replace a test method with a new implementation

    Returns:
        dict: Mapping of action base class to dict of test method names to callables/modifiers
              {
                  CreateViewActionMixin: {
                      '_test_create_post': custom_create_post_method,
                      # OR use modifiers:
                      '_test_create_post': Replace(CreateViewActionMixin, '_test_create_post', new_method),
                      '_test_some_method': Remove(CreateViewActionMixin, '_test_some_method'),
                  },
                  UpdateViewActionMixin: {
                      '_test_update_post': custom_update_post_method
                  }
              }

    Example - Basic usage:
        @hookimpl
        def djadmin_get_test_methods():
            from djadmin.actions.view_mixins import CreateViewActionMixin, UpdateViewActionMixin

            def test_formset_create_post(test_case, action):
                # Custom implementation for FormCollection POST
                url = test_case._get_action_url(action)
                data = test_case.build_formset_post_data(test_case.get_create_data())
                response = test_case.client.post(url, data, content_type='application/json')
                # ... assertions

            return {
                CreateViewActionMixin: {
                    '_test_create_post': test_formset_create_post
                },
                UpdateViewActionMixin: {
                    '_test_update_post': test_formset_update_post
                }
            }

    Example - Using modifiers:
        @hookimpl
        def djadmin_get_test_methods():
            from djadmin.actions.view_mixins import CreateViewActionMixin, UpdateViewActionMixin
            from djadmin.plugins.modifiers import Replace, Remove

            def test_formset_create_post(test_case, action):
                # Custom FormCollection implementation
                ...

            return {
                CreateViewActionMixin: {
                    # Replace core's POST test with FormCollection-specific version
                    '_test_create_post': Replace(
                        CreateViewActionMixin,
                        '_test_create_post',
                        test_formset_create_post
                    )
                },
                UpdateViewActionMixin: {
                    # Remove a test that doesn't apply
                    '_test_some_method': Remove(UpdateViewActionMixin, '_test_some_method')
                }
            }
    """
    pass


# INSTALLED_APPS management hooks
@hookspec
def djadmin_get_required_apps():
    """
    Return required INSTALLED_APPS for this plugin.

    Allows plugins to declare their required apps with ordering constraints
    using djp's Before/After modifiers for automatic dependency resolution.

    Returns:
        list: App names, potentially wrapped in ordering modifiers:
              - First('app_name')  # Load first (before everything else)
              - Before('app_name')  # Load in "before" bucket (before core apps)
              - After('app_name')  # Load in "after" bucket (after core apps)
              - Position('app_name', before='djadmin')  # Load directly before another app
              - Position('app_name', after='django.contrib.admin')  # Load directly after another app
              - 'plain_app_name'  # No ordering constraint (default bucket)

    Example - Theme plugin must load first:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import First

            return [
                First('djadmin.plugins.theme'),  # Load first for template precedence
            ]

    Example - Formset plugin with early loading:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import Before

            return [
                Before('formset'),  # Formset loads early
                'django.contrib.contenttypes',  # No constraint (default bucket)
            ]

    Example - Optional plugin loads late:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import After

            return [
                After('myapp.optional_feature'),  # Load after core apps
            ]

    Example - No special ordering:
        @hookimpl
        def djadmin_get_required_apps():
            return [
                'django_filters',  # No modifier needed
            ]

    Note:
        Ordering resolution:
        1. Collects all apps from all hook implementations
        2. First apps → first bucket (very beginning)
        3. Before apps → before bucket
        4. Normal apps → default bucket (includes djadmin core)
        5. After apps → after bucket
        6. Position apps → inserted relative to other apps
        7. Final order: [first...] + [before...] + [default...] + [after...]

    Usage:
        # settings.py
        from djadmin import djadmin_apps

        INSTALLED_APPS = [
            'django.contrib.admin',
            # ... other apps
        ] + djadmin_apps()

    Plugin Discovery:
        Built-in plugins (core, theme) are auto-registered by djadmin_apps().

        Third-party plugins must declare an entrypoint in pyproject.toml:

            [project.entry-points.djadmin]
            my_plugin = "my_plugin.djadmin_hooks"

        When djadmin_apps() is called, it:
        1. Registers built-in plugins (djadmin.plugins.core, djadmin.plugins.theme)
        2. Discovers third-party plugins via entrypoints (pm.load_setuptools_entrypoints('djadmin'))
        3. Calls djadmin_get_required_apps() on all registered plugins
        4. Resolves ordering using First/Before/After/Position modifiers

    Important:
        The theme plugin's hook only runs if the plugin is registered.
        This only happens when no other plugin provides the 'theme' feature.
        See djadmin.apps.DjAdminConfig.ready() for auto-registration logic.
    """
    pass


# Register hook specifications
pm.add_hookspecs(sys.modules[__name__])

# Expose hookimpl decorator for plugin authors (must match project name)
hookimpl = pluggy.HookimplMarker('djadmin')

__all__ = ['pm', 'hookspec', 'hookimpl', 'Remove', 'Replace', 'First', 'Before', 'After', 'Position']
