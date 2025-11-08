"""View mixins provided by the core plugin"""

from functools import cached_property

import django
from django.conf import settings
from django.db import connection
from django.db.models import Q
from django.urls import reverse

import djadmin
from djadmin.forms import FormBuilder


class RedirectViewMixin:
    """
    Mixin for RedirectView-based actions.

    Implements get_redirect_url() with method dispatch pattern:
    1. Check if action has redirect_url attribute (string URL)
    2. Otherwise delegate to action's get_redirect_url() method
    3. Otherwise call parent's get_redirect_url() (Django's default)

    This allows actions to specify redirects via either:
    - redirect_url = 'some/url'  (simple string)
    - def get_redirect_url(self, *args, **kwargs)  (dynamic method)

    The view instance (self) has:
    - self.action: Action instance
    - self.request: Current request
    - self.kwargs: URL kwargs (e.g., {'pk': 1})
    - self.args: URL args
    """

    def get_redirect_url(self, *args, **kwargs):
        """
        Get redirect URL from action or parent.

        Method dispatch order:
        1. action.redirect_url (if set and not None)
        2. action.get_redirect_url(view, *args, **kwargs) (if method exists)
        3. super().get_redirect_url() (Django's RedirectView default)

        Returns:
            URL string (absolute or relative)
        """
        # Check if action has redirect_url attribute
        redirect_url = getattr(self.action, 'redirect_url', None)
        if redirect_url is not None:
            return redirect_url

        # Check if action has get_redirect_url method
        if hasattr(self.action, 'get_redirect_url'):
            # Bind the action method to the view by passing self (view) as first arg
            # This allows the action method to access view attributes (kwargs, request, etc.)
            return self.action.get_redirect_url.__func__(self, *args, **kwargs)

        # Fallback to Django's RedirectView default
        return super().get_redirect_url(*args, **kwargs)


class DjAdminViewMixin:
    """
    Base mixin applied to all django-admin-deux views.

    Provides standard context data that all admin views need:
    - opts: Model meta
    - action: Action instance
    - model_admin: ModelAdmin instance
    - admin_site: AdminSite instance
    - list_url: URL to list view
    - action_namespace: Namespace for action URLs
    - assets: CSS/JS assets from plugins
    - djadmin_version: django-admin-deux version
    - django_version: Django version
    - general_actions, bulk_actions, record_actions: Filtered action lists

    This mixin is automatically added by the core plugin to all views.
    """

    @cached_property
    def filtered_actions(self):
        """
        Filtered action lists by user permissions, cached on view instance.

        For object-based views (UpdateView, DetailView, DeleteView), filters
        actions based on the specific object. For list views, filters at model level.

        Results are cached on the view instance, which is per-request since Django
        creates a new view instance for each request. Combined with request-level
        caching in ModelAdmin.filter_actions(), this ensures actions are filtered
        only once per request.

        Performance Impact:
            Without caching: Actions filtered multiple times per request
            With caching: Actions filtered once per request (view instance)

        Returns:
            dict: Dictionary with filtered action lists:
                  - filtered_general_actions
                  - filtered_bulk_actions
                  - filtered_record_actions
        """
        if self.model_admin is None:
            return {
                'filtered_general_actions': [],
                'filtered_bulk_actions': [],
                'filtered_record_actions': [],
            }

        # Get object if this is an object-based view
        obj = getattr(self, 'object', None)

        return {
            'filtered_general_actions': self.model_admin.filter_actions(
                self.model_admin.general_actions, self.request, obj=obj
            ),
            'filtered_bulk_actions': self.model_admin.filter_actions(
                self.model_admin.bulk_actions, self.request, obj=obj
            ),
            'filtered_record_actions': self.model_admin.filter_actions(
                self.model_admin.record_actions, self.request, obj=obj
            ),
        }

    def get_context_data(self, **kwargs):
        """
        Add standard admin context to all views.

        When bound to the view, self is the view instance which has:
        - self.action: Action instance
        - self.model: Model class
        - self.model_admin: ModelAdmin instance
        - self.admin_site: AdminSite instance
        - self.request: Current request
        """
        from djadmin.plugins import pm

        # Call super to get base context from Django CBV
        context = super().get_context_data(**kwargs)

        # Add request to context (needed for inclusion tags)
        context['request'] = self.request

        # Add standard admin context
        context['model'] = self.model
        context['opts'] = self.model._meta if self.model else None
        context['action'] = self.action
        context['model_admin'] = self.model_admin
        context['admin_site'] = self.admin_site

        # Add version information
        context['djadmin_version'] = djadmin.__version__
        context['django_version'] = django.get_version()

        # Add site-wide URLs
        try:
            context['index_url'] = reverse(f'{self.admin_site.name}:index')
        except Exception:
            context['index_url'] = '/'

        # Add site configuration
        context['site_header'] = self.admin_site.site_header
        context['site_title'] = self.admin_site.site_title
        context['index_title'] = self.admin_site.index_title

        # Add list URL (using admin_site namespace)
        # Skip for site-level actions (model=None)
        if self.model is not None:
            list_url_name = f'{self.model_admin.list_url_name}'
            context['list_url'] = self.admin_site.reverse(list_url_name)
        else:
            context['list_url'] = context.get('index_url', '/')

        # Add namespaced URL names for actions
        namespace = self.admin_site.name
        context['action_namespace'] = namespace

        # Add breadcrumbs
        context['breadcrumb_list'] = self._get_breadcrumbs()

        # Add assets from plugins
        assets = self._get_assets_from_plugins()
        context['assets'] = assets

        # Add sidebar widgets for template rendering
        sidebar_widgets = self._get_sidebar_widgets_for_template()
        context['sidebar_widgets'] = sidebar_widgets

        # Add column header icons for list views
        column_header_icons = self._get_column_header_icons()
        context['column_header_icons'] = column_header_icons

        # Add filtered actions to context (permission-checked)
        # This ensures all views (ListView, UpdateView, CreateView, etc.) get filtered actions
        if self.model is not None and self.model_admin is not None:
            # Add unfiltered action lists (for template tag use in ListView)
            context['general_actions'] = self.model_admin.general_actions
            context['bulk_actions'] = self.model_admin.bulk_actions
            context['record_actions'] = self.model_admin.record_actions

            # Add filtered action lists (for use in templates)
            context.update(self.filtered_actions)

        # Allow plugins to add more context
        plugin_contexts = pm.hook.djadmin_add_context_data(
            context=context,
            request=self.request,
            view=self,
        )

        for plugin_context in plugin_contexts:
            if plugin_context:
                context.update(plugin_context)

        if settings.DEBUG:
            # List loaded plugins for debugging
            # djp.PluginManager wraps pluggy, access the underlying manager
            try:
                # Get plugins from the underlying pluggy manager
                if hasattr(pm, '_pm'):
                    # djp stores the pluggy manager as _pm
                    plugins = pm._pm.get_plugins()
                elif hasattr(pm, 'get_plugins'):
                    plugins = pm.get_plugins()
                else:
                    # Fallback: just note that we couldn't list plugins
                    plugins = ['(plugin listing not available)']

                context['debug_loaded_plugins'] = [str(plugin) for plugin in plugins]
            except Exception as e:
                context['debug_loaded_plugins'] = [f'Error listing plugins: {e}']

            # Debug: Show view's MRO (Method Resolution Order) to see which mixins are applied
            context['debug_view_mro'] = [cls.__name__ for cls in self.__class__.__mro__[:10]]

            # Debug: Show form class being used
            if hasattr(self, 'form_class'):
                context['debug_form_class'] = str(self.form_class)

            # Debug: Show action class hierarchy
            context['debug_action_mro'] = [cls.__name__ for cls in self.action.__class__.__mro__[:10]]

        return context

    def build_form(self, form=None):
        """
        Build form class from layout or fields. Override in plugins to customize.

        This method is called by get_form_class() when no explicit form_class is provided.
        The default implementation uses FormBuilder to create forms from layouts or fields.

        Returns:
            ModelForm class ready for instantiation
        """
        layout = self.get_layout()

        if layout:
            # Build from layout using FormBuilder
            print('using FormBuilder.from_layout')
            return FormBuilder.from_layout(layout, self.model, form_class=None)

        print('using FormBuilder.create_form')
        # No layout - build from fields

        fields = getattr(self, 'get_fields', lambda: '__all__')()
        return FormBuilder.create_form(self.model, fields=fields)

    def _get_breadcrumbs(self):
        """
        Generate breadcrumb trail for the current view.

        Returns:
            List of dicts with 'title' and 'url' keys
        """
        breadcrumbs = []

        # Home/Dashboard link
        try:
            index_url = reverse(f'{self.admin_site.name}:index')
            breadcrumbs.append({'title': self.admin_site.index_title or 'Dashboard', 'url': index_url})
        except Exception:
            pass

        # Handle site-level views (model=None, e.g., dashboards)
        if self.model is None:
            # Check if this is an app dashboard (has app_label in kwargs)
            app_label = self.kwargs.get('app_label') if hasattr(self, 'kwargs') else None
            if app_label:
                # Add app breadcrumb for app dashboard
                try:
                    from django.apps import apps

                    app_config = apps.get_app_config(app_label)
                    app_verbose_name = app_config.verbose_name
                except Exception:
                    app_verbose_name = app_label.replace('_', ' ').title()

                # App dashboard is the current page, so no URL
                breadcrumbs.append({'title': app_verbose_name, 'url': None})

            return breadcrumbs

        # App dashboard link
        app_label = self.model._meta.app_label
        try:
            # Get app verbose name from AppConfig
            from django.apps import apps

            app_config = apps.get_app_config(app_label)
            app_verbose_name = app_config.verbose_name
        except Exception:
            # Fallback to formatted app_label if app config not found
            app_verbose_name = app_label.replace('_', ' ').title()

        try:
            app_url = reverse(f'{self.admin_site.name}:{app_label}_app_index')
            breadcrumbs.append({'title': app_verbose_name, 'url': app_url})
        except Exception:
            pass

        # Model list link (or current page if we're on ListView)
        verbose_name_plural = self.model._meta.verbose_name_plural
        action_label = getattr(self.action, 'label', None)

        # Check if we're currently on the list view
        if action_label == 'List':
            # On list view - show as current page (no link)
            breadcrumbs.append({'title': verbose_name_plural.capitalize(), 'url': None})
        else:
            # Not on list view - show as link
            try:
                list_url = reverse(f'{self.admin_site.name}:{self.model_admin.list_url_name}')
                breadcrumbs.append({'title': verbose_name_plural.capitalize(), 'url': list_url})
            except Exception:
                pass

            # Add current action (no link) if it's not List or View
            if action_label and action_label not in ['List', 'View']:
                breadcrumbs.append(
                    {
                        'title': action_label,
                        'url': None,  # Current page, no link
                    }
                )

        return breadcrumbs

    def _get_assets_from_plugins(self):
        """
        Get CSS/JS assets from plugins for this action.

        This method is resilient and accepts both formats from plugins:
        - Plain strings (e.g., 'djadmin/theme/css/theme.css') - backward compatible
        - CSSAsset/JSAsset objects with additional attributes (module, defer, etc.)

        All assets are normalized to CSSAsset/JSAsset objects for consistent
        template rendering with proper attributes.

        Returns:
            Dict with 'css' and 'js' keys containing lists of CSSAsset/JSAsset objects
        """
        from djadmin.dataclasses import CSSAsset, JSAsset
        from djadmin.plugins import pm

        results = pm.hook.djadmin_get_action_view_assets(action=self.action)

        assets = {'css': [], 'js': []}
        for registry in results:
            if registry:
                for action_class, asset_dict in registry.items():
                    if isinstance(self.action, action_class):
                        if asset_dict:
                            # Process CSS assets - normalize strings to CSSAsset objects
                            for css_item in asset_dict.get('css', []):
                                if isinstance(css_item, str):
                                    assets['css'].append(CSSAsset(href=css_item))
                                elif isinstance(css_item, CSSAsset):
                                    assets['css'].append(css_item)
                                else:
                                    raise TypeError(f'CSS asset must be str or CSSAsset, got {type(css_item).__name__}')

                            # Process JS assets - normalize strings to JSAsset objects
                            for js_item in asset_dict.get('js', []):
                                if isinstance(js_item, str):
                                    assets['js'].append(JSAsset(src=js_item))
                                elif isinstance(js_item, JSAsset):
                                    assets['js'].append(js_item)
                                else:
                                    raise TypeError(f'JS asset must be str or JSAsset, got {type(js_item).__name__}')

        return assets

    def _get_sidebar_widgets_for_template(self):
        """
        Prepare sidebar widgets for template rendering.

        Filters widgets based on their condition and prepares their context data.
        The template will use this data to render each widget.

        Returns:
            List of dicts with 'template' and 'context' keys for widgets
            that should be displayed in the current view.
        """
        # Get sidebar_widgets from view class (set by ViewFactory)
        widgets = getattr(self, 'sidebar_widgets', [])

        widgets_for_template = []
        for widget in widgets:
            # Check if widget should be displayed
            # Pass view instance (self) instead of action so callbacks can access view attributes
            if widget.should_display(self, self.request):
                # Get widget context
                widget_context = widget.get_context(self, self.request)

                widgets_for_template.append(
                    {
                        'template': widget.template,
                        'context': widget_context,
                        'identifier': widget.identifier,
                    }
                )

        return widgets_for_template

    def _get_column_header_icons(self):
        """
        Get column header icons from view class (set by ViewFactory).

        These icons are then processed per-column in the template using
        their condition/callable attributes to determine display and URLs.

        Returns:
            List of ColumnHeaderIcon instances, sorted by order
        """
        return getattr(self, 'column_header_icons', [])


class SearchMixin:
    """
    Mixin for ListView to add search functionality across multiple fields.

    This mixin provides database-agnostic search with smart PostgreSQL
    full-text search detection and fallback to icontains.

    Usage:
        class MyModelAdmin(ModelAdmin):
            search_fields = ['name', 'description', 'author__name']

    The mixin will:
        - Use PostgreSQL SearchVector for full-text search when available
        - Fall back to Q objects with icontains for other databases
        - Support related field lookups (e.g., 'author__name')
        - Split search query into words (Django admin pattern)
    """

    def get_search_query(self):
        """
        Get the search query from request parameters.

        Returns:
            String search query or None
        """
        return self.request.GET.get('search', '').strip()

    def get_search_fields(self):
        """
        Get the list of fields to search.

        Returns:
            List of field names from model_admin.search_fields, or empty list
        """
        return getattr(self.model_admin, 'search_fields', None) or []

    def apply_search(self, queryset):
        """
        Apply search filtering to the queryset.

        Args:
            queryset: The base queryset to filter

        Returns:
            Filtered queryset with search applied
        """
        search_query = self.get_search_query()
        search_fields = self.get_search_fields()

        if not search_query or not search_fields:
            return queryset

        # Detect if we're using PostgreSQL
        if self._is_postgresql():
            return self._apply_search_postgresql(queryset, search_query, search_fields)
        else:
            return self._apply_search_generic(queryset, search_query, search_fields)

    def _is_postgresql(self):
        """
        Check if the model's database backend is PostgreSQL.

        Returns:
            True if PostgreSQL, False otherwise
        """
        # Get the database vendor for the current connection
        # Note: Using connection.vendor is simpler and works for the default database
        # For multi-database setups, this would need enhancement
        vendor = connection.vendor

        return vendor == 'postgresql'

    def _apply_search_postgresql(self, queryset, search_query, search_fields):
        """
        Apply full-text search using PostgreSQL's SearchVector.

        Note: Falls back to generic search if any fields contain relationships (__)
        as SearchVector doesn't support Django's lookup syntax.

        Args:
            queryset: Base queryset
            search_query: Search string
            search_fields: List of field names

        Returns:
            Filtered queryset using SearchVector or generic search
        """
        # Check if any fields contain relationship lookups (__)
        has_related_fields = any('__' in field for field in search_fields)
        if has_related_fields:
            # SearchVector doesn't support __ lookups, use generic search
            return self._apply_search_generic(queryset, search_query, search_fields)

        try:
            from django.contrib.postgres.search import SearchQuery, SearchVector

            # Build SearchVector for all fields
            search_vector = SearchVector(search_fields[0])
            for field_name in search_fields[1:]:
                search_vector = search_vector + SearchVector(field_name)

            # Create SearchQuery
            search_query_obj = SearchQuery(search_query)

            # Apply search
            return queryset.annotate(search=search_vector).filter(search=search_query_obj)

        except ImportError:
            # PostgreSQL search not available, fall back to generic
            return self._apply_search_generic(queryset, search_query, search_fields)

    def _apply_search_generic(self, queryset, search_query, search_fields):
        """
        Apply search using Q objects with icontains (Django admin pattern).

        This follows Django admin's search behavior:
        - Split search query into words
        - Each word must match at least one field (OR across fields)
        - All words must be found (AND across words)

        Args:
            queryset: Base queryset
            search_query: Search string
            search_fields: List of field names

        Returns:
            Filtered queryset using Q objects
        """
        # Split search query into words
        search_terms = search_query.split()

        # Build Q objects for each word
        for term in search_terms:
            # Build OR condition across all fields for this term
            q_objects = Q()
            for field_name in search_fields:
                # Support for field lookups (e.g., 'author__name')
                lookup = f'{field_name}__icontains'
                q_objects |= Q(**{lookup: term})

            # Apply AND condition (all words must match)
            queryset = queryset.filter(q_objects)

        return queryset

    def get_queryset(self):
        """
        Get the queryset with search applied.

        This overrides ListView's get_queryset() to apply search filtering.

        Returns:
            Filtered QuerySet
        """
        # Get base queryset from parent
        queryset = super().get_queryset()

        # Apply search if configured
        return self.apply_search(queryset)
