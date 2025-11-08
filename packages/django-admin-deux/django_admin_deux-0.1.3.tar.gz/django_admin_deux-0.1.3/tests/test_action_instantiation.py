"""Tests for action instantiation in ModelAdmin."""

import pytest

from djadmin.actions.base import BaseAction, BulkActionMixin, GeneralActionMixin, RecordActionMixin
from djadmin.options import ModelAdmin
from examples.webshop.models import Product


class CustomListAction(GeneralActionMixin, BaseAction):
    """Custom list action for testing."""

    label = 'Custom List Action'

    def execute(self, request, **kwargs):
        return None


class CustomBulkAction(BulkActionMixin, BaseAction):
    """Custom bulk action for testing."""

    label = 'Custom Bulk Action'

    def execute(self, request, queryset, **kwargs):
        return None


class CustomRecordAction(RecordActionMixin, BaseAction):
    """Custom record action for testing."""

    label = 'Custom Record Action'

    def execute(self, request, obj, **kwargs):
        return None


@pytest.mark.django_db
class TestActionInstantiation:
    """Test that ModelAdmin properly instantiates action classes."""

    def test_plugin_default_actions_instantiated(self, admin_site):
        """Plugin-provided default actions should be instantiated."""

        class ProductAdmin(ModelAdmin):
            # No actions specified - should get plugin defaults
            pass

        admin = ProductAdmin(Product, admin_site)

        # Should have plugin-provided defaults (currently empty list, but that's OK)
        assert isinstance(admin.general_actions, list)
        assert isinstance(admin.bulk_actions, list)
        assert isinstance(admin.record_actions, list)

        # All actions should be instances, not classes
        for action in admin.general_actions:
            assert not isinstance(action, type), f'Expected instance, got class: {action}'
            assert hasattr(action, 'model')
            assert action.model == Product
            assert hasattr(action, 'model_admin')
            assert action.model_admin is admin
            assert hasattr(action, 'admin_site')
            assert action.admin_site is admin_site

    def test_user_defined_actions_instantiated(self, admin_site):
        """User-defined action classes should be instantiated."""

        class ProductAdmin(ModelAdmin):
            general_actions = [CustomListAction]
            bulk_actions = [CustomBulkAction]
            record_actions = [CustomRecordAction]

        admin = ProductAdmin(Product, admin_site)

        # Should have exactly one of each type
        assert len(admin.general_actions) == 1
        assert len(admin.bulk_actions) == 1
        assert len(admin.record_actions) == 1

        # All should be instances with correct types
        assert type(admin.general_actions[0]).__name__ == 'CustomListAction'
        assert type(admin.bulk_actions[0]).__name__ == 'CustomBulkAction'
        assert type(admin.record_actions[0]).__name__ == 'CustomRecordAction'

        # All should have correct context
        for action in admin.general_actions + admin.bulk_actions + admin.record_actions:
            assert not isinstance(action, type), f'Expected instance, got class: {action}'
            assert action.model == Product
            assert action.model_admin is admin
            assert action.admin_site is admin_site

    def test_mixed_classes_and_instances(self, admin_site):
        """Should handle mix of action classes and pre-instantiated actions."""

        # Pre-instantiate one action
        pre_instantiated = CustomListAction(Product, None, admin_site)

        class ProductAdmin(ModelAdmin):
            general_actions = [CustomListAction, pre_instantiated]

        admin = ProductAdmin(Product, admin_site)

        # Should have two actions
        assert len(admin.general_actions) == 2

        # Both should be instances
        for action in admin.general_actions:
            assert not isinstance(action, type)
            assert type(action).__name__ == 'CustomListAction'

        # First one should have the admin as model_admin (freshly instantiated)
        assert admin.general_actions[0].model_admin is admin

        # Second one should keep its original model_admin (None in this case)
        assert admin.general_actions[1].model_admin is None

    def test_empty_user_actions_override_plugins(self, admin_site):
        """User can explicitly set empty action lists to override plugins."""

        class ProductAdmin(ModelAdmin):
            general_actions = []  # Explicitly empty
            bulk_actions = []
            record_actions = []

        admin = ProductAdmin(Product, admin_site)

        # Should respect user's explicit empty lists
        assert admin.general_actions == []
        assert admin.bulk_actions == []
        assert admin.record_actions == []

    def test_action_instances_can_access_model_admin(self, admin_site):
        """Action instances should be able to access their model_admin."""

        class ProductAdmin(ModelAdmin):
            general_actions = [CustomListAction]
            paginate_by = 42  # Custom setting

        admin = ProductAdmin(Product, admin_site)

        action = admin.general_actions[0]

        # Action should have access to model_admin configuration
        assert action.model_admin.paginate_by == 42
        assert action.model_admin.model == Product

    def test_multiple_instances_of_same_action_class(self, admin_site):
        """Should be able to have multiple instances of the same action class."""

        class ProductAdmin(ModelAdmin):
            general_actions = [CustomListAction, CustomListAction]

        admin = ProductAdmin(Product, admin_site)

        # Should have two distinct instances
        assert len(admin.general_actions) == 2
        assert admin.general_actions[0] is not admin.general_actions[1]
        assert isinstance(admin.general_actions[0], type(admin.general_actions[1]))

    def test_action_label_accessible(self, admin_site):
        """Action labels should be accessible from instances."""

        class ProductAdmin(ModelAdmin):
            general_actions = [CustomListAction]

        admin = ProductAdmin(Product, admin_site)

        action = admin.general_actions[0]
        assert action.label == 'Custom List Action'
