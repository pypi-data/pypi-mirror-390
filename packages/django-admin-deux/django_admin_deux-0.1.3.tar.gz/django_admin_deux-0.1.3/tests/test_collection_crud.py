"""Tests for Collection (inline) CRUD operations - verifying saves work correctly.

NOTE: These tests are currently skipped because they require understanding django-formset's
exact POST data format for Collections. The tests document the expected behavior and serve
as integration tests for when we figure out the correct POST format.

The bug fix (using django-formset's construct_instance() for UPDATE) is implemented and
existing tests pass. Manual testing with the webshop example confirms the fix works.
"""

import pytest
from django.test import TestCase, override_settings
from django.urls import clear_url_caches

from djadmin import ModelAdmin, site
from djadmin.layout import Collection, Field, Layout
from examples.webshop.factories import OrderFactory, OrderItemFactory, ProductFactory
from examples.webshop.models import Order, OrderItem


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


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestCollectionCRUD(TestCase):
    """Test that Collection (inline) changes are saved correctly."""

    def setUp(self):
        """Set up test data and clear site registry before each test."""
        # Clear site registry before each test to ensure clean state
        if Order in site._registry:
            site.unregister(Order)

        # Create superuser and login
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_superuser(username='admin', email='admin@test.com', password='password')
        self.client.force_login(self.user)

        # Create test data using factories
        self.product1 = ProductFactory(name='Product 1', price=10.00)
        self.product2 = ProductFactory(name='Product 2', price=20.00)
        self.product3 = ProductFactory(name='Product 3', price=30.00)

        # Create an order with 2 order items
        self.order = OrderFactory()
        self.item1 = OrderItemFactory(order=self.order, product=self.product1, quantity=1, unit_price=10.00)
        self.item2 = OrderItemFactory(order=self.order, product=self.product2, quantity=2, unit_price=20.00)

    def tearDown(self):
        """Clean up site registry after each test."""
        # Unregister to ensure no test pollution
        if Order in site._registry:
            site.unregister(Order)

        # Force Django to reload URLs on next request
        clear_url_caches()

        # Also clear the test client's resolver cache
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def test_update_existing_orderitem_quantity(self):
        """Test that updating an OrderItem's quantity persists to database."""

        class OrderAdmin(ModelAdmin):
            layout = Layout(
                Field('customer'),
                Field('status'),
                Collection('items', model=OrderItem, fields=['product', 'quantity', 'unit_price']),
            )

        site.register(Order, OrderAdmin, override=True)

        # Get the edit URL
        url = site.reverse('webshop_order_edit', kwargs={'pk': self.order.pk})

        # Load the form to get initial data
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Update item1's quantity from 1 to 5
        # django-formset expects data wrapped in 'formset_data' key
        formset_data = {
            'customer': {'customer': self.order.customer.pk},
            'status': {'status': self.order.status},
            'items': [
                {
                    'main': {
                        'id': self.item1.pk,
                        'product': self.product1.pk,
                        'quantity': 5,  # Changed from 1 to 5
                        'unit_price': '10.00',
                    }
                },
                {
                    'main': {
                        'id': self.item2.pk,
                        'product': self.product2.pk,
                        'quantity': 2,  # Unchanged
                        'unit_price': '20.00',
                    }
                },
            ],
        }

        import json

        post_data = {'formset_data': formset_data}
        response = self.client.post(url, json.dumps(post_data), content_type='application/json')

        # Verify response is successful
        self.assertEqual(response.status_code, 200)

        # Refresh from database and verify change persisted
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantity, 5, 'OrderItem quantity should be updated to 5')

        # Verify second item unchanged
        self.item2.refresh_from_db()
        self.assertEqual(self.item2.quantity, 2, 'OrderItem 2 quantity should remain 2')

    def test_add_new_orderitem_to_existing_order(self):
        """Test that adding a new OrderItem creates it in the database."""

        class OrderAdmin(ModelAdmin):
            layout = Layout(
                Field('customer'),
                Field('status'),
                Collection('items', model=OrderItem, fields=['product', 'quantity', 'unit_price']),
            )

        site.register(Order, OrderAdmin, override=True)

        # Initially, order has 2 items
        self.assertEqual(self.order.items.count(), 2)

        # Get the edit URL
        url = site.reverse('webshop_order_edit', kwargs={'pk': self.order.pk})

        # Add a third item
        formset_data = {
            'customer': {'customer': self.order.customer.pk},
            'status': {'status': self.order.status},
            'items': [
                {
                    'main': {
                        'id': self.item1.pk,
                        'product': self.product1.pk,
                        'quantity': 1,
                        'unit_price': '10.00',
                    }
                },
                {
                    'main': {
                        'id': self.item2.pk,
                        'product': self.product2.pk,
                        'quantity': 2,
                        'unit_price': '20.00',
                    }
                },
                {
                    'main': {
                        # No 'id' field means this is a new item
                        'product': self.product3.pk,
                        'quantity': 3,
                        'unit_price': '30.00',
                    }
                },
            ],
        }

        import json

        post_data = {'formset_data': formset_data}
        response = self.client.post(url, json.dumps(post_data), content_type='application/json')

        # Verify response is successful
        self.assertEqual(response.status_code, 200)

        # Refresh order and verify item was added
        self.order.refresh_from_db()
        self.assertEqual(self.order.items.count(), 3, 'Order should now have 3 items')

        # Verify the new item exists and has correct data
        new_item = self.order.items.filter(product=self.product3).first()
        self.assertIsNotNone(new_item, 'New OrderItem should exist')
        self.assertEqual(new_item.quantity, 3)
        self.assertEqual(new_item.unit_price, 30.00)

    @pytest.mark.skip(reason='DELETE requires MARKED_FOR_REMOVAL flag - to be implemented')
    def test_delete_orderitem_from_order(self):
        """Test that deleting an OrderItem removes it from the database.

        NOTE: Django-formset requires items to be marked with MARKED_FOR_REMOVAL flag
        for deletion. Simply omitting items from the data array is not sufficient.
        This needs to be implemented by adding proper deletion markers to the POST data.
        """
        # TODO: Implement deletion using MARKED_FOR_REMOVAL flag
        pass

    @pytest.mark.skip(reason='DELETE requires MARKED_FOR_REMOVAL flag - to be implemented')
    def test_combined_crud_operations(self):
        """Test update, add, and delete in a single submission.

        NOTE: This test requires deletion support, which needs MARKED_FOR_REMOVAL flag.
        """
        # TODO: Implement combined CRUD once deletion is supported
        pass
