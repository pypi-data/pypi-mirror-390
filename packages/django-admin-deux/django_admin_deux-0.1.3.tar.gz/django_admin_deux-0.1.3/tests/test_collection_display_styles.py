"""Tests for Collection display_style parameter."""

from django.test import TestCase

from djadmin import ModelAdmin, site
from djadmin.layout import Collection, Field, Layout
from examples.webshop.models import Order, OrderItem


class TestCollectionDisplayStyles(TestCase):
    """Test Collection display_style parameter and rendering."""

    def setUp(self):
        """Clean registry."""
        if Order in site._registry:
            site.unregister(Order)

    def tearDown(self):
        """Clean up."""
        if Order in site._registry:
            site.unregister(Order)

    def test_collection_default_display_style_is_tabular(self):
        """Collection should default to tabular display style."""
        collection = Collection('items', model=OrderItem, fields=['product'])
        self.assertEqual(collection.display_style, 'tabular')

    def test_collection_accepts_tabular_display_style(self):
        """Collection should accept display_style='tabular'."""
        collection = Collection('items', model=OrderItem, fields=['product'], display_style='tabular')
        self.assertEqual(collection.display_style, 'tabular')

    def test_collection_accepts_stacked_display_style(self):
        """Collection should accept display_style='stacked'."""
        collection = Collection('items', model=OrderItem, fields=['product'], display_style='stacked')
        self.assertEqual(collection.display_style, 'stacked')

    def test_collection_rejects_invalid_display_style(self):
        """Collection should reject invalid display_style values."""
        with self.assertRaises(ValueError) as cm:
            Collection('items', model=OrderItem, fields=['product'], display_style='compact')

        self.assertIn("must be 'tabular' or 'stacked'", str(cm.exception))
        self.assertIn("'compact'", str(cm.exception))

    def test_model_admin_can_use_mixed_display_styles(self):
        """ModelAdmin can have Collections with different display styles."""

        class OrderAdmin(ModelAdmin):
            layout = Layout(
                Field('customer'),
                Collection(
                    'orderitem_set',
                    model=OrderItem,
                    fields=['product', 'quantity'],
                    display_style='tabular',
                ),
                Collection(
                    'orderitem_set',
                    model=OrderItem,
                    fields=['note'],
                    display_style='stacked',
                ),
            )

        admin = OrderAdmin(Order, site)

        # Get collections from layout
        collections = [c for c in admin.layout.items if isinstance(c, Collection)]

        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0].display_style, 'tabular')
        self.assertEqual(collections[1].display_style, 'stacked')
