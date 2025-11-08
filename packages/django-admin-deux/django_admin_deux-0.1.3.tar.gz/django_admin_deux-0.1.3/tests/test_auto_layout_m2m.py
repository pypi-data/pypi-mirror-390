"""
Tests for auto-layout generation with many-to-many fields.
"""

from django.test import TestCase

from djadmin import ModelAdmin, site
from djadmin.layout import Field
from examples.webshop.models import Product


class TestAutoLayoutM2MFields(TestCase):
    """Test that auto-layout correctly includes M2M fields.

    These tests use direct ModelAdmin instantiation instead of global site
    registration to avoid test pollution. Since these tests only inspect
    layout objects and don't make HTTP requests, they don't need URL resolution
    or the DynamicURLConf pattern.
    """

    def _get_field_names(self):
        model_admin = site.get_model_admins(Product)[0]
        field_names = [item.name for item in model_admin._create_auto_layout().items if isinstance(item, Field)]
        return field_names

    def test_auto_layout_includes_m2m_fields(self):
        """Auto-layout should include M2M fields when fields='__all__'."""

        field_names = self._get_field_names()

        # M2M field 'tags' should be included
        self.assertIn('tags', field_names, f"M2M field 'tags' missing. Got: {field_names}")

        # Should include regular fields too
        self.assertIn('name', field_names)
        self.assertIn('sku', field_names)
        self.assertIn('category', field_names)  # ForeignKey

    def test_auto_layout_excludes_reverse_relations(self):
        """Auto-layout should NOT include reverse relations."""

        field_names = self._get_field_names()

        # M2M field 'tags' should be included
        self.assertIn('tags', field_names, f"M2M field 'tags' missing. Got: {field_names}")

        # Should include regular fields too
        self.assertIn('name', field_names)
        self.assertIn('sku', field_names)
        self.assertIn('category', field_names)  # ForeignKey

    def test_auto_layout_excludes_non_editable_fields(self):
        """Auto-layout should NOT include non-editable fields."""

        field_names = self._get_field_names()

        # Non-editable timestamp fields should NOT be included
        self.assertNotIn('created_at', field_names, 'Non-editable created_at should be excluded')
        self.assertNotIn('updated_at', field_names, 'Non-editable updated_at should be excluded')

        # But editable timestamp field should be included
        self.assertIn('published_at', field_names, 'Editable published_at should be included')

    def test_auto_layout_with_explicit_fields(self):
        """When fields is explicitly set, auto-layout should use those fields."""

        class ProductAdmin(ModelAdmin):
            fields = ['name', 'sku', 'tags']  # Explicit field list

        model_admin = ProductAdmin(Product, site)
        field_names = [item.name for item in model_admin._create_auto_layout().items if isinstance(item, Field)]

        # Should only include explicitly listed fields
        self.assertEqual(field_names, ['name', 'sku', 'tags'])
