"""Tests for Django admin inline compatibility layer."""

import warnings

from django.test import TestCase
from django.urls import clear_url_caches

from djadmin import ModelAdmin, StackedInline, TabularInline, site
from djadmin.layout import Collection
from examples.webshop.models import Order, OrderItem


class TestInlineCompatibility(TestCase):
    """Test Django-style inline classes work with automatic conversion."""

    def setUp(self):
        """Clean up site registry before each test."""
        if Order in site._registry:
            site.unregister(Order)

    def tearDown(self):
        """Clean up after tests."""
        if Order in site._registry:
            site.unregister(Order)
        clear_url_caches()
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def test_tabular_inline_converts_to_collection_with_tabular_style(self):
        """TabularInline should convert to Collection with display_style='tabular'."""

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            class OrderItemInline(TabularInline):
                model = OrderItem
                fields = ['product', 'quantity', 'unit_price']
                extra = 2
                min_num = 1
                max_num = 20

            class OrderAdmin(ModelAdmin):
                inlines = [OrderItemInline]

            admin = OrderAdmin(Order, site)

            # Should emit deprecation warnings
            # One from __init_subclass__, one from _process_inlines_to_layout
            self.assertGreaterEqual(len(w), 1)
            # Check for the ModelAdmin.inlines deprecation warning
            inlines_warnings = [warning for warning in w if 'inlines is deprecated' in str(warning.message)]
            self.assertEqual(len(inlines_warnings), 1)

        # Check Collection has tabular display style
        collections = [c for c in admin.layout.items if isinstance(c, Collection)]
        self.assertEqual(len(collections), 1)
        collection = collections[0]
        self.assertEqual(collection.display_style, 'tabular')

    def test_stacked_inline_converts_to_collection_with_stacked_style(self):
        """StackedInline should convert to Collection with display_style='stacked'."""

        class OrderItemInline(StackedInline):
            model = OrderItem
            fields = ['product', 'quantity', 'unit_price']
            extra = 1

        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')

            class OrderAdmin(ModelAdmin):
                inlines = [OrderItemInline]

            admin = OrderAdmin(Order, site)

        # Check Collection has stacked display style
        collections = [c for c in admin.layout.items if isinstance(c, Collection)]
        self.assertEqual(len(collections), 1)
        collection = collections[0]
        self.assertEqual(collection.display_style, 'stacked')

    def test_mixed_tabular_and_stacked_inlines(self):
        """Can mix TabularInline and StackedInline in same ModelAdmin."""

        class TabularOrderItemInline(TabularInline):
            model = OrderItem
            fields = ['product', 'quantity']

        # Create a separate inline with different fields to avoid conflicts
        class StackedOrderItemInline(StackedInline):
            model = OrderItem
            fields = ['product', 'unit_price']

        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')

            class OrderAdmin(ModelAdmin):
                inlines = [TabularOrderItemInline, StackedOrderItemInline]

            admin = OrderAdmin(Order, site)

        collections = [c for c in admin.layout.items if isinstance(c, Collection)]
        self.assertEqual(len(collections), 2)

        # First should be tabular
        self.assertEqual(collections[0].display_style, 'tabular')
        self.assertEqual(collections[0].fields, ['product', 'quantity'])

        # Second should be stacked
        self.assertEqual(collections[1].display_style, 'stacked')
        self.assertEqual(collections[1].fields, ['product', 'unit_price'])

    def test_collection_display_style_parameter_validation(self):
        """Collection should validate display_style parameter."""
        # Valid values should work
        Collection('items', model=OrderItem, fields=['product'], display_style='tabular')
        Collection('items', model=OrderItem, fields=['product'], display_style='stacked')

        # Invalid values should raise
        with self.assertRaises(ValueError) as cm:
            Collection('items', model=OrderItem, fields=['product'], display_style='invalid')

        self.assertIn("must be 'tabular' or 'stacked'", str(cm.exception))

    def test_collection_repr_includes_display_style(self):
        """Collection repr should include display_style if not default."""
        # Tabular (default) - not shown in repr
        col_tabular = Collection('items', model=OrderItem, fields=['product'], display_style='tabular')
        self.assertNotIn('display_style', repr(col_tabular))

        # Stacked (non-default) - shown in repr
        col_stacked = Collection('items', model=OrderItem, fields=['product'], display_style='stacked')
        self.assertIn("display_style='stacked'", repr(col_stacked))

    def test_inline_all_attributes_mapped_correctly(self):
        """All inline attributes should map to Collection parameters."""

        class OrderItemInline(TabularInline):
            model = OrderItem
            fields = ['product', 'quantity', 'unit_price']
            extra = 2
            min_num = 1
            max_num = 20
            verbose_name_plural = 'Line Items'

        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')

            class OrderAdmin(ModelAdmin):
                inlines = [OrderItemInline]

            admin = OrderAdmin(Order, site)

        collections = [c for c in admin.layout.items if isinstance(c, Collection)]
        collection = collections[0]

        # Check all mappings
        self.assertEqual(collection.model, OrderItem)
        self.assertEqual(collection.fields, ['product', 'quantity', 'unit_price'])
        self.assertEqual(collection.extra_siblings, 2)
        self.assertEqual(collection.min_siblings, 1)
        self.assertEqual(collection.max_siblings, 20)
        self.assertEqual(collection.legend, 'Line Items')
        self.assertEqual(collection.display_style, 'tabular')
