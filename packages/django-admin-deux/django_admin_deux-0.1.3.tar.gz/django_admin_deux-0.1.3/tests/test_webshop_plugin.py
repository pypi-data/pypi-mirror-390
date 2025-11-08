"""Test the webshop test plugin"""

import pytest
from django.test import RequestFactory

from djadmin import AdminSite, ModelAdmin
from djadmin.factories import ViewFactory
from djadmin.plugins import pm
from djadmin.plugins.core.actions import ListAction
from examples.webshop.factories import ProductFactory
from examples.webshop.models import Product
from tests.factories import UserFactory


@pytest.mark.django_db
class TestWebshopPlugin:
    """Test the webshop queryset modification plugin"""

    def test_webshop_plugin_loaded(self):
        """Webshop plugin should be discovered and loaded"""
        features = set()
        for feature_list in pm.hook.djadmin_provides_features():
            features.update(feature_list or [])

        assert 'active_filter' in features

    def test_plugin_does_not_modify_queryset_without_parameter(self):
        """Plugin should not filter when parameter is not set"""
        admin_site = AdminSite()

        # Create test data
        ProductFactory.create_batch(5, status='active')
        ProductFactory.create_batch(3, status='draft')

        class ProductAdmin(ModelAdmin):
            list_display = ['name', 'status']

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/')

        view = view_class()
        view.request = request
        view.kwargs = {}

        queryset = view.get_queryset()

        # Without parameter - should see all products
        assert queryset.count() == 8

    def test_plugin_modifies_queryset_with_parameter(self):
        """Plugin should filter to active products when parameter is set"""
        admin_site = AdminSite()

        # Create test data
        ProductFactory.create_batch(5, status='active')
        ProductFactory.create_batch(3, status='draft')

        class ProductAdmin(ModelAdmin):
            list_display = ['name', 'status']

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/?active_only=1')

        view = view_class()
        view.request = request
        view.kwargs = {}

        queryset = view.get_queryset()

        # With parameter - should see only active
        assert queryset.count() == 5
        assert all(p.status == 'active' for p in queryset)

    def test_plugin_adds_context(self):
        """Plugin should add context variables"""
        admin_site = AdminSite()
        ProductFactory.create_batch(3, status='active')

        class ProductAdmin(ModelAdmin):
            list_display = ['name']

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        assert 'webshop_plugin_active' in context
        assert context['webshop_plugin_active'] is True

        # Check filter state
        assert 'active_filter_enabled' in context
        assert context['active_filter_enabled'] is False

    def test_plugin_context_with_filter(self):
        """Plugin context should reflect filter state"""
        admin_site = AdminSite()
        ProductFactory.create_batch(3, status='active')

        class ProductAdmin(ModelAdmin):
            list_display = ['name']

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/?active_only=1')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        # With filter parameter
        assert context['active_filter_enabled'] is True

    def test_plugin_only_affects_product_model(self):
        """Plugin should only modify Product queryset, not other models"""
        from examples.webshop.factories import CategoryFactory
        from examples.webshop.models import Category

        admin_site = AdminSite()

        CategoryFactory.create_batch(5)

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']

        admin_site.register(Category, CategoryAdmin)
        model_admin = admin_site._registry[Category][0]

        action = ListAction(Category, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/category/?active_only=1')

        view = view_class()
        view.request = request
        view.kwargs = {}

        queryset = view.get_queryset()

        # Should not filter categories (plugin only affects Product)
        assert queryset.count() == 5
