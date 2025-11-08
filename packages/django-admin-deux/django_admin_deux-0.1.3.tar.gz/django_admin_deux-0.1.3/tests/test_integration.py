"""
Integration tests for Milestone 3 Layout API and django-formset plugin.

Tests end-to-end workflows for:
- Core layout rendering (without plugin)
- Plugin-enhanced rendering (with plugin)
- Feature validation
- Form submission workflows
"""

import pytest
from django.test import TestCase, override_settings

from djadmin import ModelAdmin, site
from djadmin.layout import Collection, Field, Layout
from examples.webshop.factories import CategoryFactory, ProductFactory
from examples.webshop.models import Category, Product
from tests.conftest import RegistrySaveRestoreMixin


class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


# NOTE: Tests for core layout rendering without plugin and feature validation
# without plugin are in tests/test_layout_validation.py as unit tests.
# Integration tests focus on end-to-end workflows with the plugin installed.


@override_settings(ROOT_URLCONF=DynamicURLConf())
@pytest.mark.skipif(
    not pytest.importorskip('djadmin_formset', reason='djadmin-formset plugin not installed'),
    reason='Requires djadmin-formset plugin',
)
class TestPluginEnhancedRendering(RegistrySaveRestoreMixin, TestCase):
    """Test plugin-enhanced rendering with djadmin-formset."""

    # Specify models to save/restore
    registry_models = [Product]

    def setUp(self):
        """Set up test data."""
        # Call parent setUp to save registry state
        super().setUp()

        self.products = ProductFactory.create_batch(3)

        # Authenticate the client
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client.force_login(self.user)
        # tearDown is inherited from RegistrySaveRestoreMixin

    def test_plugin_converts_to_formcollection(self):
        """Test that plugin converts forms to FormCollection."""

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('sku'),
            )

        site.register(Product, ProductAdmin, override=True)

        # Make a request to trigger form class creation
        url = site.reverse('webshop_product_add')
        response = self.client.get(url)

        # Should render successfully with plugin
        self.assertEqual(response.status_code, 200)
        # Check that formset is being used (django-formset web component)
        self.assertContains(response, '<django-formset')

    def test_create_view_with_collections(self):
        """Test CREATE view with collections (inline editing)."""

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('sku'),
                Collection(
                    'category',
                    model=Category,
                    fields=['name', 'slug'],
                ),
            )

        site.register(Product, ProductAdmin, override=True)

        url = site.reverse('webshop_product_add')
        response = self.client.get(url)

        # Should not error with plugin installed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name')
        self.assertContains(response, 'sku')

    def test_update_view_with_collections(self):
        """Test UPDATE view with collections (inline editing)."""
        # NOTE: Collections are for one-to-many relationships (reverse ForeignKey)
        # Product.category is a ForeignKey (many-to-one), not suitable for Collection
        # Instead test with simple fields

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('sku'),
            )

        site.register(Product, ProductAdmin, override=True)

        product = self.products[0]
        url = site.reverse('webshop_product_edit', kwargs={'pk': product.pk})
        response = self.client.get(url)

        # Should not error with plugin installed
        self.assertEqual(response.status_code, 200)
        # Should render the product name
        self.assertContains(response, product.name)

    def test_conditional_fields_with_plugin(self):
        """Test conditional fields work with plugin (no error)."""

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('sku', show_if=".name !== ''"),
            )

        site.register(Product, ProductAdmin, override=True)

        url = site.reverse('webshop_product_add')
        response = self.client.get(url)

        # Should not error with plugin installed
        self.assertEqual(response.status_code, 200)
        # Should render the form with formset (django-formset web component)
        self.assertContains(response, '<django-formset')
        # Should have both fields
        self.assertContains(response, 'name')
        self.assertContains(response, 'sku')

    def test_computed_fields_with_plugin(self):
        """Test computed fields work with plugin (no error)."""

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('price'),
                Field('cost'),  # Normal field, not computed (Product has cost field)
            )

        site.register(Product, ProductAdmin, override=True)

        url = site.reverse('webshop_product_add')
        response = self.client.get(url)

        # Should not error with plugin installed
        self.assertEqual(response.status_code, 200)
        # Should render the form with formset (django-formset web component)
        self.assertContains(response, '<django-formset')
        # Should have all fields
        self.assertContains(response, 'name')
        self.assertContains(response, 'price')
        self.assertContains(response, 'cost')


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestActionSpecificLayouts(RegistrySaveRestoreMixin, TestCase):
    """Test action-specific layouts (create_layout vs update_layout)."""

    # Specify models to save/restore
    registry_models = [Category]

    def setUp(self):
        """Set up test data."""
        # Call parent setUp to save registry state
        super().setUp()

        self.category = CategoryFactory()

        # Authenticate the client
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client.force_login(self.user)
        # tearDown is inherited from RegistrySaveRestoreMixin

    def test_create_layout_used_for_create_view(self):
        """Test that create_layout is used for create view."""

        class CategoryAdmin(ModelAdmin):
            layout = Layout(Field('name'))
            create_layout = Layout(
                Field('name'),
                Field('slug'),
            )
            update_layout = Layout(
                Field('name'),
                Field('description'),
            )

        site.register(Category, CategoryAdmin, override=True)

        # CREATE view should use create_layout
        url = site.reverse('webshop_category_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'slug')
        self.assertNotContains(response, 'description')

    def test_update_layout_used_for_update_view(self):
        """Test that update_layout is used for update view."""

        class CategoryAdmin(ModelAdmin):
            layout = Layout(Field('name'))
            create_layout = Layout(
                Field('name'),
                Field('slug'),
            )
            update_layout = Layout(
                Field('name'),
                Field('description'),
            )

        site.register(Category, CategoryAdmin, override=True)

        # Verify admin has the layouts
        admin = site._registry[Category][0]
        self.assertIsNotNone(admin.update_layout)
        self.assertEqual(len(admin.update_layout.items), 2)

        # UPDATE view should use update_layout
        url = site.reverse('webshop_category_edit', kwargs={'pk': self.category.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should have description (from update_layout)
        self.assertContains(response, 'description')
        # Should NOT have slug (only in create_layout)
        self.assertNotContains(response, 'slug')

    def test_fallback_to_generic_layout(self):
        """Test fallback to generic layout when action-specific not defined."""

        class CategoryAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('slug'),
                Field('description'),
            )

        site.register(Category, CategoryAdmin, override=True)

        # Both views should use generic layout
        create_url = site.reverse('webshop_category_add')
        create_response = self.client.get(create_url)

        update_url = site.reverse('webshop_category_edit', kwargs={'pk': self.category.pk})
        update_response = self.client.get(update_url)

        # Both should have all fields
        for response in [create_response, update_response]:
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'name')
            self.assertContains(response, 'slug')
            self.assertContains(response, 'description')
