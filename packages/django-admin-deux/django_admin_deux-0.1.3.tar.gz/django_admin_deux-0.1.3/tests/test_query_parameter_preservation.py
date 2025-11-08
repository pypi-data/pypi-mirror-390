"""Integration tests for combined filter, order, search, and pagination functionality."""

from django.test import TestCase, override_settings

from djadmin import Column, ModelAdmin, site
from djadmin.dataclasses import Filter
from examples.webshop.factories import CategoryFactory, ProductFactory
from examples.webshop.models import Category, Product
from tests.conftest import RegistrySaveRestoreMixin


class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [path('djadmin/', include(site.urls))]


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestQueryParameterPreservation(RegistrySaveRestoreMixin, TestCase):
    """Test that query parameters are properly preserved across all features."""

    # Specify models to save/restore
    registry_models = [Product, Category]

    def setUp(self):
        """Set up test data."""
        # Call parent setUp to save registry state
        super().setUp()

        # Create test data
        self.electronics = CategoryFactory(name='Electronics')
        self.books = CategoryFactory(name='Books')

        # Create products with varied data
        self.laptop = ProductFactory(name='Laptop Pro', category=self.electronics, price=1200, status='active')
        self.phone = ProductFactory(name='Smartphone X', category=self.electronics, price=800, status='active')
        self.tablet = ProductFactory(name='Tablet Mini', category=self.electronics, price=400, status='active')
        self.novel = ProductFactory(name='Python Programming', category=self.books, price=50, status='active')
        self.cookbook = ProductFactory(name='Django Cookbook', category=self.books, price=45, status='active')

        # Authenticate the client
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client.force_login(self.user)
        # tearDown is inherited from RegistrySaveRestoreMixin

    def test_filter_preserves_search_and_ordering(self):
        """Test that applying filters preserves search and ordering parameters."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name', filter=Filter(lookup_expr='icontains'), order=True),
                Column('price', filter=True, order=True),
                Column('category', filter=True),
            ]
            search_fields = ['name', 'category__name']

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Start with search and ordering
        response = self.client.get(url, {'search': 'Pro', 'ordering': '-price'})
        self.assertEqual(response.status_code, 200)

        # Now add filter - should preserve search and ordering
        response = self.client.get(url, {'search': 'Pro', 'ordering': '-price', 'category': self.electronics.id})
        self.assertEqual(response.status_code, 200)

        products = list(response.context['object_list'])
        # Should have laptop (matches "Pro" and electronics category)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.laptop)

        # Verify parameters are in response context
        self.assertEqual(response.context['request'].GET.get('search'), 'Pro')
        self.assertEqual(response.context['request'].GET.get('ordering'), '-price')
        self.assertEqual(response.context['request'].GET.get('category'), str(self.electronics.id))

    def test_search_preserves_filters_and_ordering(self):
        """Test that searching preserves filter and ordering parameters."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name', filter=True, order=True),
                Column('category', filter=True),
                Column('status', filter=True),
            ]
            search_fields = ['name']

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Start with filters and ordering
        response = self.client.get(url, {'category': self.electronics.id, 'ordering': 'name'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 3)  # 3 electronics products

        # Now add search - should preserve filters and ordering
        response = self.client.get(
            url, {'search': 'Pro', 'category': self.electronics.id, 'ordering': 'name', 'status': 'active'}
        )
        self.assertEqual(response.status_code, 200)

        products = list(response.context['object_list'])
        # Should have laptop only (matches "Pro", electronics, and active)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.laptop)

    def test_ordering_preserves_search_and_filters(self):
        """Test that changing ordering preserves search and filter parameters."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name', filter=True, order=True),
                Column('price', filter=True, order=True),
                Column('category', filter=True),
            ]
            search_fields = ['name']

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Start with search and filters
        response = self.client.get(url, {'search': 'o', 'category': self.books.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)  # 2 books (both contain 'o')

        # Now add ordering - should preserve search and filters
        response = self.client.get(url, {'search': 'o', 'category': self.books.id, 'ordering': 'price'})
        self.assertEqual(response.status_code, 200)

        products = list(response.context['object_list'])
        # Should be ordered by price (cookbook $45, novel $50)
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0], self.cookbook)
        self.assertEqual(products[1], self.novel)

    def test_pagination_preserves_all_parameters(self):
        """Test that pagination preserves search, filter, and ordering parameters."""
        # Create many products
        for i in range(25):
            ProductFactory(name=f'Electronics Item {i}', category=self.electronics, price=100 + i, status='active')

        class ProductAdmin(ModelAdmin):
            list_display = [Column('name', filter=True, order=True), Column('category', filter=True)]
            search_fields = ['name']
            paginate_by = 10

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Apply search, filter, and ordering
        response = self.client.get(
            url, {'search': 'Electronics', 'category': self.electronics.id, 'ordering': '-price'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])

        # Go to page 2 - should preserve all parameters
        response = self.client.get(
            url, {'search': 'Electronics', 'category': self.electronics.id, 'ordering': '-price', 'page': 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)

        # Verify all parameters preserved
        self.assertEqual(response.context['request'].GET.get('search'), 'Electronics')
        self.assertEqual(response.context['request'].GET.get('category'), str(self.electronics.id))
        self.assertEqual(response.context['request'].GET.get('ordering'), '-price')

    def test_clear_search_preserves_filters_and_ordering(self):
        """Test that clearing search preserves filters and ordering."""

        class ProductAdmin(ModelAdmin):
            list_display = [Column('name', filter=True, order=True), Column('category', filter=True)]
            search_fields = ['name']

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Start with all parameters
        response = self.client.get(url, {'search': 'Pro', 'category': self.electronics.id, 'ordering': 'name'})
        self.assertEqual(response.status_code, 200)

        # Clear search - should preserve filters and ordering
        response = self.client.get(url, {'category': self.electronics.id, 'ordering': 'name'})
        self.assertEqual(response.status_code, 200)

        # Should have all electronics products, no search filter
        products = list(response.context['object_list'])
        self.assertEqual(len(products), 3)
        # Verify ordering still applied
        self.assertEqual(products[0], self.laptop)  # "Laptop" comes first alphabetically

    def test_clear_filters_preserves_search_and_ordering(self):
        """Test that clearing filters preserves search and ordering."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name', filter=True, order=True),
                Column('category', filter=True),
                Column('status', filter=True),
            ]
            search_fields = ['name']

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Start with all parameters
        response = self.client.get(
            url, {'search': 'Pro', 'category': self.electronics.id, 'status': 'active', 'ordering': '-price'}
        )
        self.assertEqual(response.status_code, 200)

        # Clear filters - should preserve search and ordering
        response = self.client.get(url, {'search': 'Pro', 'ordering': '-price'})
        self.assertEqual(response.status_code, 200)

        # Should match all products with "Pro" in name, ordered by price descending
        products = list(response.context['object_list'])
        self.assertGreater(len(products), 0)
        # Verify search still applied
        for product in products:
            self.assertIn('Pro', product.name)

    def test_all_features_combined(self):
        """Test all features working together: search + filter + order + pagination."""
        # Create enough products for pagination
        for i in range(25):
            ProductFactory(name=f'Product {i}', category=self.electronics, price=100 + i + i, status='active')

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name', filter=Filter(lookup_expr='icontains'), order=True),
                Column('price', filter=True, order=True),
                Column('category', filter=True),
                Column('status', filter=True),
            ]
            search_fields = ['name']
            paginate_by = 10

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('webshop_product_list')

        # Apply all features at once
        response = self.client.get(
            url,
            {
                'search': 'Product',
                'category': self.electronics.id,
                'status': 'active',
                'ordering': '-price',
                'page': 2,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['page_obj'].number, 2)

        # Verify all parameters are present
        request_get = response.context['request'].GET
        self.assertEqual(request_get.get('search'), 'Product')
        self.assertEqual(request_get.get('category'), str(self.electronics.id))
        self.assertEqual(request_get.get('status'), 'active')
        self.assertEqual(request_get.get('ordering'), '-price')
        self.assertEqual(request_get.get('page'), '2')

        # Verify results are filtered and ordered correctly
        products = list(response.context['object_list'])
        self.assertGreater(len(products), 0)
        # All should be from electronics category, active status, and match "Product"
        for product in products:
            self.assertEqual(product.category, self.electronics)
            self.assertEqual(product.status, 'active')
            self.assertIn('Product', product.name)
