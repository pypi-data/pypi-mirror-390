"""Tests for pagination functionality"""

import pytest
from django.test import RequestFactory

from djadmin import AdminSite, ModelAdmin
from djadmin.factories import ViewFactory
from djadmin.plugins.core.actions import ListAction
from examples.webshop.factories import ProductFactory
from examples.webshop.models import Product
from tests.factories import UserFactory


@pytest.mark.django_db
class TestPagination:
    """Test pagination in ListView"""

    def test_pagination_applied(self):
        """Pagination should be applied to ListView"""
        admin_site = AdminSite()

        # Create more products than paginate_by
        ProductFactory.create_batch(150)

        class ProductAdmin(ModelAdmin):
            paginate_by = 100

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        # Create action and generate view
        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}

        # Get page 1
        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert 'page_obj' in context
        assert 'paginator' in context
        assert context['paginator'].num_pages == 2
        assert context['page_obj'].number == 1
        assert len(context['page_obj'].object_list) == 100

    def test_pagination_page_2(self):
        """Should be able to access page 2"""
        admin_site = AdminSite()
        ProductFactory.create_batch(150)

        class ProductAdmin(ModelAdmin):
            paginate_by = 100

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/?page=2')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}

        view.object_list = view.get_queryset()
        context = view.get_context_data()

        assert context['page_obj'].number == 2
        assert len(context['page_obj'].object_list) == 50

    def test_pagination_custom_page_size(self):
        """Should respect custom paginate_by"""
        admin_site = AdminSite()
        ProductFactory.create_batch(100)

        class ProductAdmin(ModelAdmin):
            paginate_by = 25

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

        assert context['paginator'].per_page == 25
        assert context['paginator'].num_pages == 4

    def test_pagination_context_helpers(self):
        """Should add pagination helper context"""
        admin_site = AdminSite()
        ProductFactory.create_batch(200)

        class ProductAdmin(ModelAdmin):
            paginate_by = 20

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/?page=5')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}

        view.object_list = view.get_queryset()
        context = view.get_context_data()

        # Check pagination helpers are added
        assert 'page_range' in context
        assert 'show_first' in context
        assert 'show_last' in context

        # Check page_range contains page numbers
        assert 1 in context['page_range']
        assert 5 in context['page_range']  # Current page
        assert 10 in context['page_range']  # Last page

    def test_pagination_page_range_ellipsis(self):
        """Page range should include ellipsis for large page counts"""
        admin_site = AdminSite()
        ProductFactory.create_batch(500)

        class ProductAdmin(ModelAdmin):
            paginate_by = 10

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        factory = RequestFactory()
        request = factory.get('/djadmin/webshop/product/?page=25')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks

        view = view_class()
        view.request = request
        view.kwargs = {}

        view.object_list = view.get_queryset()
        context = view.get_context_data()

        page_range = context['page_range']

        # Should have ellipsis (None) in range
        assert None in page_range

        # Should show current page and neighbors
        assert 25 in page_range
        assert 24 in page_range
        assert 26 in page_range

    def test_no_pagination_helpers_when_not_paginated(self):
        """Should not add pagination helpers when not paginated"""
        admin_site = AdminSite()
        ProductFactory.create_batch(5)

        class ProductAdmin(ModelAdmin):
            paginate_by = 100  # More than total records

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

        # Should not be paginated
        assert not context.get('is_paginated')

        # Pagination helpers should not be added (or be empty)
        # The core plugin returns {} when not paginated
        assert 'page_range' not in context or not context.get('page_range')
