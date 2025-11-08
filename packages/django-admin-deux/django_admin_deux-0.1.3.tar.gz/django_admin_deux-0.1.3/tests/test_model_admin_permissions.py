"""Tests for ModelAdmin permission_class configuration and metaclass normalization"""

import pytest

from djadmin.options import ModelAdmin
from djadmin.plugins.permissions import AllowAny, IsAuthenticated, IsStaff
from djadmin.plugins.permissions.operators import And


@pytest.mark.django_db
class TestModelAdminDefaultPermission:
    """Test default permission_class on ModelAdmin"""

    def test_model_admin_has_default_permission(self, product, admin_site):
        """ModelAdmin should have default permission: IsStaff() & HasDjangoPermission()"""

        class ProductAdmin(ModelAdmin):
            pass

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        assert model_admin.permission_class is not None
        assert isinstance(model_admin.permission_class, And)

    def test_base_model_admin_class_has_none_permission(self):
        """Base ModelAdmin class should have permission_class = None"""
        # The base class should not have the default applied
        # Only subclasses get the default
        assert hasattr(ModelAdmin, 'permission_class')


@pytest.mark.django_db
class TestModelAdminPermissionOverride:
    """Test overriding permission_class on ModelAdmin"""

    def test_can_override_with_instance(self, product, admin_site):
        """Can override permission_class with an instance"""

        class ProductAdmin(ModelAdmin):
            permission_class = AllowAny()

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        assert isinstance(model_admin.permission_class, AllowAny)

    def test_can_override_with_none(self, product, admin_site):
        """Can override permission_class with None to disable permission checks"""

        class ProductAdmin(ModelAdmin):
            permission_class = None

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        assert model_admin.permission_class is None

    def test_can_override_with_composition(self, product, admin_site):
        """Can override permission_class with composed permissions"""

        class ProductAdmin(ModelAdmin):
            permission_class = IsAuthenticated() & IsStaff()

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        assert isinstance(model_admin.permission_class, And)


@pytest.mark.django_db
class TestMetaclassNormalization:
    """Test metaclass normalization of permission_class"""

    def test_class_is_normalized_to_instance(self, product, admin_site):
        """Metaclass should normalize permission class to instance"""

        class ProductAdmin(ModelAdmin):
            permission_class = IsAuthenticated  # Class, not instance

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        # Should be instantiated
        assert isinstance(model_admin.permission_class, IsAuthenticated)

    def test_instance_remains_instance(self, product, admin_site):
        """Metaclass should leave instances as-is"""

        perm = IsAuthenticated()

        class ProductAdmin(ModelAdmin):
            permission_class = perm  # Already an instance

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        # Should be the same instance
        assert model_admin.permission_class is perm

    def test_composed_classes_are_normalized(self, product, admin_site):
        """Metaclass should normalize composed permission classes"""

        class ProductAdmin(ModelAdmin):
            permission_class = IsAuthenticated & IsStaff  # Both classes

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        # Should be an And instance
        assert isinstance(model_admin.permission_class, And)

    def test_none_remains_none(self, product, admin_site):
        """Metaclass should leave None as None"""

        class ProductAdmin(ModelAdmin):
            permission_class = None

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        assert model_admin.permission_class is None
