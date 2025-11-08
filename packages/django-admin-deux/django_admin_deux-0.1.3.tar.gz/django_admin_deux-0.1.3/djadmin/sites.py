from collections import defaultdict
from collections.abc import Iterable

import django
from django.core.exceptions import ImproperlyConfigured
from django.urls import path
from django.views.generic import TemplateView

import djadmin


class AdminSite:
    """
    An AdminSite object encapsulates an instance of the djadmin application,
    ready to be hooked into your URLconf.
    """

    def __init__(self, name='djadmin'):
        self.name = name
        self._registry = defaultdict(list)  # model_class: list[model_admin_instance]

        # Site configuration (similar to Django admin)
        self.site_header = f'{name.title()} Administration'
        self.site_title = f'{name.title()} Admin'
        self.index_title = 'Site administration'

    def register(self, model_or_iterable, admin_class=None, override=False):
        """
        Register the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelAdmin (the default).

        Note: For decorator usage, use the @register decorator from djadmin.decorators instead.

        Args:
            model_or_iterable: A model class or iterable of model classes
            admin_class: The admin class to register (defaults to ModelAdmin)
            override: If True, replaces all existing registrations for the model.
                     If False (default), adds to existing registrations.
        """
        from djadmin.options import ModelAdmin

        if admin_class is None:
            admin_class = ModelAdmin

        # Handle both single model and iterable of models
        if isinstance(model_or_iterable, Iterable) and not isinstance(model_or_iterable, str):
            models = list(model_or_iterable)
        else:
            models = [model_or_iterable]

        for model in models:
            # Instantiate the admin class
            admin_instance = admin_class(model, self)

            # Handle override mode
            if override:
                self._registry[model] = [admin_instance]
            else:
                self._registry[model].append(admin_instance)

    def unregister(self, model_or_iterable, admin_class=None):
        """
        Unregister the given model(s).

        Args:
            model_or_iterable: A model class or iterable of model classes
            admin_class: Optional. If provided, only unregister this specific admin class.
                        If None, unregister all admin classes for the model.
        """
        if isinstance(model_or_iterable, Iterable) and not isinstance(model_or_iterable, str):
            models = list(model_or_iterable)
        else:
            models = [model_or_iterable]

        for model in models:
            if model not in self._registry or not self._registry[model]:
                raise ImproperlyConfigured(f'The model {model.__name__} is not registered.')

            if admin_class is None:
                # Remove all registrations for this model
                del self._registry[model]
            else:
                # Remove only the specific admin class
                self._registry[model] = [admin for admin in self._registry[model] if not isinstance(admin, admin_class)]

                # If no registrations left, remove the model entry
                if not self._registry[model]:
                    del self._registry[model]

    def is_registered(self, model):
        """Check if a model is registered."""
        return model in self._registry and len(self._registry[model]) > 0

    def get_model_admins(self, model):
        """Get all admin classes registered for a model."""
        return self._registry.get(model, [])

    def get_urls(self):
        """Generate URL patterns for this admin site"""
        urlpatterns = [
            # Project dashboard (single for the entire admin site)
            path('', self.index, name='index'),
        ]

        # Collect all unique app labels from registered models
        app_labels = {model._meta.app_label for model in self._registry.keys()}

        # Add app dashboard URLs (one per app)
        for app_label in app_labels:
            urlpatterns.append(
                path(
                    f'{app_label}/',
                    self.app_index,
                    name=f'{app_label}_app_index',
                    kwargs={'app_label': app_label},
                )
            )

        # Add model-specific URLs
        # Support multiple admins per model with different URLs
        for model, admin_list in self._registry.items():
            if not admin_list:
                continue

            app_label = model._meta.app_label

            # Generate URLs for each registered admin
            from djadmin.factories import ViewFactory

            for model_admin in admin_list:
                # Add action URLs for this model admin
                # General actions (main entry points - no record selection needed)
                for action in model_admin.general_actions:
                    # Get URL pattern and name from the action itself
                    url_pattern = action.get_url_pattern()
                    url_name = action.url_name

                    # General actions use ViewFactory to generate views
                    factory = ViewFactory()
                    view = factory.create_view(action).as_view()

                    urlpatterns.append(
                        path(
                            url_pattern,
                            view,
                            name=url_name,
                        )
                    )

                # Record actions (operate on single record)
                for action in model_admin.record_actions:
                    # Get URL pattern and name from the action itself
                    url_pattern = action.get_url_pattern()
                    url_name = action.url_name

                    # All actions use ViewFactory
                    view = ViewFactory().create_view(action).as_view()
                    urlpatterns.append(
                        path(
                            url_pattern,
                            view,
                            name=url_name,
                        )
                    )

                # Bulk actions (operate on multiple selected records)
                for action in model_admin.bulk_actions:
                    # Get URL pattern and name from the action itself
                    url_pattern = action.get_url_pattern()
                    url_name = action.url_name

                    # All actions use ViewFactory
                    view = ViewFactory().create_view(action).as_view()
                    urlpatterns.append(
                        path(
                            url_pattern,
                            view,
                            name=url_name,
                        )
                    )

        return urlpatterns

    @property
    def urls(self):
        """
        Return URL patterns for include().

        Returns a 2-tuple (urlpatterns, app_name) that Django's include() uses to set up
        URL namespacing. The app_name serves as both the application namespace and the
        instance namespace.

        Usage:
            # In your URLconf:
            from djadmin import site

            urlpatterns = [
                path('admin/', include(site.urls)),
            ]

            # Then use reverse lookups with the site name as namespace:
            reverse('djadmin:index')
            reverse('djadmin:webshop_product_list')
        """
        return (self.get_urls(), self.name)

    def reverse(self, viewname, kwargs=None, args=None):
        """
        Reverse a URL within this admin site's namespace.

        Args:
            viewname: View name (without namespace prefix)
            kwargs: URL kwargs
            args: URL args

        Returns:
            Reversed URL string
        """
        from django.urls import reverse

        # Prepend the site's namespace
        namespaced_view = f'{self.name}:{viewname}'
        return reverse(namespaced_view, kwargs=kwargs, args=args)

    def _get_base_context(self, request=None):
        """Get base context data available to all views."""
        context = {
            'site_title': self.name.title(),
            'site_header': self.name.title(),
            'djadmin_version': djadmin.__version__,
            'django_version': django.get_version(),
        }
        # Add the index URL - use absolute path as fallback if namespace not available
        if request:
            try:
                from django.urls import reverse

                context['index_url'] = reverse(f'{self.name}:index')
            except Exception:
                # Fallback to root path if reverse fails
                context['index_url'] = '/'
        return context

    def index(self, request):
        """Project dashboard view (action-based)."""
        from djadmin.actions.dashboard import DashboardAction
        from djadmin.factories import ViewFactory

        action = DashboardAction(admin_site=self)
        factory = ViewFactory()
        view_class = factory.create_view(action)
        return view_class.as_view()(request)

    def app_index(self, request, app_label):
        """App dashboard view (action-based)."""
        from djadmin.actions.dashboard import DashboardAction
        from djadmin.factories import ViewFactory

        action = DashboardAction(admin_site=self)
        factory = ViewFactory()
        view_class = factory.create_view(action)
        return view_class.as_view()(request, app_label=app_label)

    def placeholder_view(self, request, model, view_type, pk=None):
        """Placeholder for model list views."""
        context = self._get_base_context(request)
        context['opts'] = model._meta
        if pk:
            context['pk'] = pk
        view = TemplateView.as_view(
            template_name='djadmin/model_list.html',
            extra_context=context,
        )
        return view(request)


# Default admin site instance
site = AdminSite()
