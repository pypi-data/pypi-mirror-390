"""Tests for RedirectActionMixin and RedirectViewActionMixin"""

from django.test import TestCase, override_settings
from django.urls import clear_url_caches

from djadmin import site
from djadmin.actions import BaseAction, RecordActionMixin
from djadmin.actions.view_mixins import RedirectViewActionMixin
from examples.webshop.factories import ProductFactory
from examples.webshop.models import Product


# Dynamic URLconf that regenerates URLs on each request
# This allows tests to register/unregister admins and see fresh URLs
class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


class ExternalLinkAction(RecordActionMixin, RedirectViewActionMixin, BaseAction):
    """Example redirect action that redirects to an external URL."""

    label = 'View External'
    icon = 'external-link'

    def get_url_pattern(self) -> str:
        """URL pattern for this action."""
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/<int:pk>/actions/external/'

    def get_redirect_url(self, *args, **kwargs):
        """
        Redirect to external URL based on URL kwargs.

        When bound to view, self is the view instance with:
        - self.kwargs: URL kwargs including 'pk'
        - self.request: The current request
        """
        # RedirectView doesn't have get_object(), so use pk from kwargs
        pk = self.kwargs.get('pk')
        return f'https://example.com/products/{pk}'


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestRedirectAction(TestCase):
    """Test RedirectActionMixin with RedirectViewActionMixin."""

    def setUp(self):
        """Set up test data and admin."""
        from djadmin import ModelAdmin
        from tests.factories import UserFactory

        # Save existing registry state before test
        self._original_registry = site._registry.get(Product, []).copy()

        # Clear site registry before each test to ensure clean state
        if site.is_registered(Product):
            site.unregister(Product)

        # Create test user and log in
        self.user = UserFactory(is_staff=True, is_superuser=True)
        self.client.force_login(self.user)

        # Create test product
        self.product = ProductFactory()

        # Register admin with redirect action
        class ProductAdmin(ModelAdmin):
            record_actions = [ExternalLinkAction]

        site.register(Product, ProductAdmin, override=True)

    def tearDown(self):
        """Clean up site registry after each test."""
        # Restore original registry state
        if self._original_registry:
            site._registry[Product] = self._original_registry
        elif Product in site._registry:
            del site._registry[Product]

        # Force Django to reload URLs on next request
        clear_url_caches()

        # Also clear the test client's resolver cache
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def test_redirect_action_redirects(self):
        """Test that redirect action performs redirect."""
        # Get the action instance (already instantiated)
        model_admin = site._registry[Product][0]
        action = model_admin.record_actions[0]

        # Get the action URL
        url = site.reverse(action.url_name, kwargs={'pk': self.product.pk})

        # Make request
        response = self.client.get(url)

        # Should redirect to external URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'https://example.com/products/{self.product.pk}')

    def test_redirect_action_has_correct_base_class(self):
        """Test that ViewFactory generates RedirectView as base class."""
        from django.views.generic import RedirectView

        # Get the action instance (already instantiated)
        model_admin = site._registry[Product][0]
        action = model_admin.record_actions[0]

        # Get the view class
        view_class = action.get_view_class()

        # Should be based on RedirectView
        self.assertTrue(
            issubclass(view_class, RedirectView),
            f'View class should inherit from RedirectView, got: {view_class.__mro__}',
        )

    def test_redirect_action_binds_get_redirect_url(self):
        """Test that get_redirect_url is bound from action to view."""
        # Get the action instance (already instantiated)
        model_admin = site._registry[Product][0]
        action = model_admin.record_actions[0]

        # Get the view class
        view_class = action.get_view_class()

        # Should have get_redirect_url method
        self.assertTrue(
            hasattr(view_class, 'get_redirect_url'), 'View class should have get_redirect_url method from action'
        )
