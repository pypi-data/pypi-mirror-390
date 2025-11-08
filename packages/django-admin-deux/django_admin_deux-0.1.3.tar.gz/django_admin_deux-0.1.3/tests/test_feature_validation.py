import pytest
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from djadmin import ModelAdmin
from examples.webshop.models import Product


def test_validation_passes_without_features(admin_site):
    """ModelAdmin with no features should validate"""

    class ProductAdmin(ModelAdmin):
        list_display = ['name', 'sku']

    admin_site.register(Product, ProductAdmin)
    # Should not raise - no validation error


def test_validation_fails_with_missing_features(monkeypatch):
    """ModelAdmin with unsupported features should fail validation"""
    from djadmin.sites import site as default_site

    # Clear existing registrations
    default_site._registry.clear()

    class ProductAdmin(ModelAdmin):
        search_fields = ['name', 'sku']  # Requires 'search' feature

    default_site.register(Product, ProductAdmin)

    # Get the djadmin app config
    config = apps.get_app_config('djadmin')

    # Mock the plugin features to exclude 'search'
    from djadmin.plugins import pm

    def mock_provides():
        return [['crud', 'theme']]  # Exclude 'search'

    monkeypatch.setattr(pm.hook, 'djadmin_provides_features', mock_provides)

    # This should raise because no plugin provides 'search'
    with pytest.raises(ImproperlyConfigured) as exc_info:
        config._validate_model_admins()

    error_msg = str(exc_info.value)
    assert 'search' in error_msg
    assert 'ProductAdmin' in error_msg
    assert 'webshop.Product' in error_msg

    # Cleanup
    default_site._registry.clear()


def test_validation_passes_with_provided_features():
    """ModelAdmin features that are provided should validate"""
    from djadmin.sites import site as default_site

    # Clear existing registrations
    default_site._registry.clear()

    class ProductAdmin(ModelAdmin):
        list_display = ['name', 'sku']
        # Don't set any features that require plugins

    default_site.register(Product, ProductAdmin)

    # Get the djadmin app config
    config = apps.get_app_config('djadmin')
    # Should not raise
    config._validate_model_admins()

    # Cleanup
    default_site._registry.clear()


def test_validation_multiple_missing_features(monkeypatch):
    """Validation should report all missing features"""
    from djadmin.sites import site as default_site

    # Clear existing registrations
    default_site._registry.clear()

    class ProductAdmin(ModelAdmin):
        search_fields = ['name']
        list_filter = ['status']
        ordering = ['-created_at']

    default_site.register(Product, ProductAdmin)

    # Get the djadmin app config
    config = apps.get_app_config('djadmin')

    # Mock to provide only 'crud' and 'theme'
    from djadmin.plugins import pm

    def mock_provides():
        return [['crud', 'theme']]

    monkeypatch.setattr(pm.hook, 'djadmin_provides_features', mock_provides)

    with pytest.raises(ImproperlyConfigured) as exc_info:
        config._validate_model_admins()

    error_msg = str(exc_info.value)
    # Should mention all missing features
    assert 'search' in error_msg
    assert 'filter' in error_msg
    assert 'ordering' in error_msg

    # Cleanup
    default_site._registry.clear()


def test_validation_with_empty_registry():
    """Validation should pass when no models are registered"""
    from djadmin.sites import site as default_site

    # Clear existing registrations
    default_site._registry.clear()

    # Get the djadmin app config
    config = apps.get_app_config('djadmin')
    # Should not raise - no models to validate
    config._validate_model_admins()

    # Cleanup
    default_site._registry.clear()


def test_validation_checks_all_registered_admins(monkeypatch):
    """Validation should check all registered ModelAdmins, not just the first"""
    from djadmin.sites import site as default_site
    from examples.webshop.models import Category

    # Clear existing registrations
    default_site._registry.clear()

    # Register first ModelAdmin without features
    class ProductAdmin1(ModelAdmin):
        list_display = ['name', 'sku']

    default_site.register(Product, ProductAdmin1)

    # Register second ModelAdmin with unsupported feature
    class CategoryAdmin(ModelAdmin):
        search_fields = ['name']  # Requires 'search' feature

    default_site.register(Category, CategoryAdmin)

    # Get the djadmin app config
    config = apps.get_app_config('djadmin')

    # Mock to provide only 'crud' and 'theme'
    from djadmin.plugins import pm

    def mock_provides():
        return [['crud', 'theme']]

    monkeypatch.setattr(pm.hook, 'djadmin_provides_features', mock_provides)

    # Should raise for the second ModelAdmin
    with pytest.raises(ImproperlyConfigured) as exc_info:
        config._validate_model_admins()

    error_msg = str(exc_info.value)
    assert 'search' in error_msg
    assert 'CategoryAdmin' in error_msg

    # Cleanup
    default_site._registry.clear()
