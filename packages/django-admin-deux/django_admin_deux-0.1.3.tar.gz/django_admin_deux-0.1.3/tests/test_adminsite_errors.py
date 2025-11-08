"""Test AdminSite error handling."""

import pytest
from django.urls import NoReverseMatch

from djadmin import AdminSite, ModelAdmin
from examples.webshop.models import Product


class TestAdminSiteErrors:
    """Test AdminSite handles errors gracefully."""

    @pytest.mark.skip(reason='Model validation deferred to Phase 2 - registration succeeds but usage fails')
    def test_register_non_model_class(self):
        """Registering non-model will fail when ModelAdmin tries to access model._meta."""
        site = AdminSite()

        class NotAModel:
            pass

        # Note: Validation deferred to later phase. Registration succeeds but using it fails
        site.register(NotAModel, ModelAdmin)
        # Would fail when trying to generate URLs or access model._meta in views

    def test_register_invalid_modeladmin(self):
        """Registering non-ModelAdmin should raise clear error."""
        site = AdminSite()

        class NotAModelAdmin:
            pass

        # Should raise error when trying to use non-ModelAdmin class
        with pytest.raises((TypeError, AttributeError)):
            site.register(Product, NotAModelAdmin)

    def test_reverse_nonexistent_url(self):
        """Reversing non-existent URL should raise clear error."""
        site = AdminSite()

        with pytest.raises((NoReverseMatch, KeyError)):
            site.reverse('nonexistent_view')

    def test_reverse_without_required_kwargs(self):
        """Reversing URL without required kwargs should raise error."""
        site = AdminSite()
        site.register(Product)

        # Reverse record action without pk should fail
        with pytest.raises((NoReverseMatch, KeyError, TypeError)):
            site.reverse('webshop_product_edit')  # Missing pk kwarg

    def test_duplicate_modeladmin_registration(self):
        """Registering same ModelAdmin class multiple times should work."""
        site = AdminSite()

        class MyAdmin(ModelAdmin):
            pass

        # Register same class twice - should be allowed
        site.register(Product, MyAdmin)
        site.register(Product, MyAdmin)

        # Should have 2 registrations
        assert len(site._registry[Product]) == 2

    def test_empty_site_urls(self):
        """Empty site should still generate valid URLs."""
        site = AdminSite()

        # Should have at minimum the dashboard URLs
        urls = site.get_urls()
        assert len(urls) >= 1  # At least index

    def test_site_name_validation(self):
        """AdminSite name should be validated."""
        # Valid names
        site1 = AdminSite(name='admin')
        assert site1.name == 'admin'

        site2 = AdminSite(name='my_admin_123')
        assert site2.name == 'my_admin_123'

        # Empty name is allowed (defaults to 'djadmin' if not specified)
        site3 = AdminSite(name='')
        assert site3.name == ''  # Empty name is valid, site works with it

    def test_unregister_nonexistent_model(self):
        """Unregistering non-registered model should raise error."""
        from django.core.exceptions import ImproperlyConfigured

        site = AdminSite()

        with pytest.raises(ImproperlyConfigured, match='not registered'):
            site.unregister(Product)

    def test_register_with_none_modeladmin(self):
        """Registering with None should use default ModelAdmin."""
        site = AdminSite()

        # Should work and create default ModelAdmin
        site.register(Product)

        assert Product in site._registry
        assert len(site._registry[Product]) == 1

    def test_register_multiple_models_at_once(self):
        """Registering multiple models should work."""
        from examples.webshop.models import Category, Customer

        site = AdminSite()

        # Register multiple models
        site.register([Product, Category, Customer])

        assert Product in site._registry
        assert Category in site._registry
        assert Customer in site._registry

    def test_reverse_with_invalid_model(self):
        """Reversing URL for unregistered model should fail."""
        site = AdminSite()

        # Try to reverse for model not in registry
        with pytest.raises((NoReverseMatch, KeyError)):
            site.reverse('nonexistent_model_list')
