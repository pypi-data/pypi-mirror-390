"""Test utilities for django-admin-deux.

This module provides base test classes that automate common testing patterns,
reducing boilerplate and ensuring consistent test coverage across ModelAdmin
implementations.

Milestone 5 Phase 2.5 adds automatic permission enforcement testing.
"""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from djadmin import site as default_site
from djadmin.sites import AdminSite

User = get_user_model()


class BaseCRUDTestCase(TestCase):
    """
    Base test case for automatically testing CRUD operations with permission enforcement.

    This class provides automatic tests for all CRUD operations by introspecting
    registered actions and running appropriate tests based on their base classes.
    It uses factory_boy for test data generation and dramatically reduces test
    boilerplate while ensuring comprehensive coverage.

    NEW in Phase 2.5: Automatic permission enforcement testing. When
    test_permission_enforcement=True (default), each test runs twice:
    1. With authentication (should succeed)
    2. Without authentication (should fail with 403 or redirect)

    Usage:
        class TestMyModelAdmin(BaseCRUDTestCase):
            model = MyModel
            model_factory_class = MyModelFactory

            # Optional customization
            factory_default_kwargs = {}
            factory_delete_kwargs = {}
            to_update_fields = {'name': 'Updated'}
            admin_site = custom_site  # Defaults to djadmin.site

            # Permission enforcement (NEW in Phase 2.5)
            test_permission_enforcement = True  # Test auth + no-auth (default)
            create_superuser = True  # Use superuser (default)
            create_staff_user = False  # Alternative: use staff user
            setup_permissions = False  # Auto-assign permissions to staff user
            permission_class_override = None  # Override ModelAdmin.permission_class

    Automatically provides:
        - test_actions() - Introspects all actions and runs appropriate tests
        - Permission enforcement testing (if test_permission_enforcement=True)

    Tests run per action type:
        - CreateViewActionMixin: GET form, POST create
        - UpdateViewActionMixin: GET form, POST update
        - DeleteViewActionMixin: POST delete

    Customization hooks:
        - get_factory_kwargs() - Customize factory creation kwargs
        - get_create_data() - Customize POST data for create
        - get_update_data() - Customize POST data for update
        - assert_create_successful() - Additional assertions after create
        - assert_update_successful() - Additional assertions after update
        - assert_delete_successful() - Additional assertions after delete
    """

    # Disable test discovery for base class
    __test__ = False

    # Required attributes (set by subclass)
    model: type[models.Model] | None = None
    model_factory_class: type | None = None

    # Optional attributes
    factory_default_kwargs: dict[str, Any] = {}
    factory_delete_kwargs: dict[str, Any] = {}
    to_update_fields: dict[str, Any] = {}
    admin_site: AdminSite | None = None

    # Permission enforcement configuration (Milestone 5 Phase 2.5)
    test_permission_enforcement: bool = True  # Test both auth and no-auth scenarios
    create_superuser: bool = True  # Use superuser (bypasses all permissions)
    create_staff_user: bool = False  # Alternative: use staff user (permission-based)
    setup_permissions: bool = False  # Auto-assign model permissions to staff user
    permission_class_override: Any = None  # Override ModelAdmin.permission_class for testing

    # Test methods are provided by plugins via djadmin_get_test_methods hook
    # This allows plugins to override test behavior for actions they modify

    def __init_subclass__(cls, **kwargs):
        """Automatically enable test discovery for concrete subclasses.

        The base class (BaseCRUDTestCase) won't be discovered, but any subclass
        that sets both model and model_factory_class will be automatically discovered.
        """
        super().__init_subclass__(**kwargs)
        # Enable test discovery only if this is a concrete implementation
        cls.__test__ = cls.model is not None and cls.model_factory_class is not None

    @classmethod
    def setUpClass(cls):
        """Set up admin site and create user for authentication."""
        super().setUpClass()
        if cls.admin_site is None:
            cls.admin_site = default_site

        # Create user for authentication (Milestone 5 Phase 2.5)
        if cls.create_superuser:
            cls.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
        elif cls.create_staff_user:
            cls.user = User.objects.create_user(
                username='staff', email='staff@example.com', password='staff123', is_staff=True
            )

            # Set up permissions if requested
            if cls.setup_permissions and cls.model:
                cls._setup_model_permissions()
        else:
            # Neither flag set - default to superuser
            cls.user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')

    @classmethod
    def _setup_model_permissions(cls):
        """Set up model permissions for the staff user.

        Assigns all CRUD permissions (add, change, delete, view) for the test model
        to the staff user.
        """
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(cls.model)
        perms = Permission.objects.filter(content_type=content_type)
        cls.user.user_permissions.add(*perms)

    def setUp(self):
        """Create test object and login user."""
        super().setUp()

        if self.model is None:
            raise ValueError('model attribute must be set')
        if self.model_factory_class is None:
            raise ValueError('model_factory_class attribute must be set')

        # Login the user (Milestone 5 Phase 2.5)
        # Only if running in full Django test context (has client and user)
        if hasattr(self, 'client') and hasattr(self, 'user'):
            self.client.force_login(self.user)

        # Create test object
        kwargs = self.get_factory_kwargs()
        self.obj = self.model_factory_class.create(**kwargs)

        # Apply permission_class override if set (Milestone 5 Phase 2.5)
        if self.permission_class_override is not None:
            try:
                model_admin = self._get_model_admin()
                model_admin.permission_class = self.permission_class_override
            except ValueError:
                # Model not registered yet - skip override
                pass

    def get_factory_kwargs(self) -> dict[str, Any]:
        """Get kwargs for factory creation.

        Override this method to customize factory creation.

        Returns:
            Dictionary of kwargs to pass to factory.create()
        """
        return self.factory_default_kwargs.copy()

    def get_factory_delete_kwargs(self) -> dict[str, Any]:
        """Get kwargs for creating object to delete.

        Override this method to create objects with different attributes
        for deletion testing.

        Returns:
            Dictionary of kwargs to pass to factory.create() for delete test
        """
        return self.factory_delete_kwargs.copy() if self.factory_delete_kwargs else self.get_factory_kwargs()

    def _get_model_admin(self):
        """Get the ModelAdmin instance for this model.

        Returns:
            ModelAdmin instance registered for this model

        Raises:
            ValueError: If model is not registered
        """
        admin_list = self.admin_site._registry.get(self.model, [])
        if not admin_list:
            raise ValueError(f'Model {self.model} is not registered with admin site')
        # Use the first registered admin (most tests only have one)
        return admin_list[0]

    def _get_all_actions(self) -> list:
        """Get all actions from the ModelAdmin.

        Returns:
            List of all action instances (general, bulk, record)
        """
        model_admin = self._get_model_admin()
        all_actions = []

        # Collect actions from all types
        all_actions.extend(model_admin.general_actions)
        all_actions.extend(model_admin.bulk_actions)
        all_actions.extend(model_admin.record_actions)

        return all_actions

    def _get_action_url(self, action, obj: models.Model | None = None) -> str:
        """Get URL for an action.

        Args:
            action: Action instance
            obj: Optional model instance (for record actions)

        Returns:
            URL path for the action
        """
        kwargs = {'pk': obj.pk} if obj else {}
        return self.admin_site.reverse(action.url_name, kwargs=kwargs)

    def _get_test_methods_mapping(self) -> dict[type, dict[str, Callable]]:
        """Get test methods mapping from plugins.

        Processes test methods from all plugins and applies modifiers (Remove, Replace).
        Plugins are processed in order, with later plugins able to override earlier ones.

        Returns:
            Dictionary mapping action base classes to test method dictionaries.
            Each test method dict maps method names to callables.
        """
        from djadmin.plugins import pm
        from djadmin.plugins.modifiers import BaseModifier

        # Collect test methods from all plugins
        plugin_test_methods = pm.hook.djadmin_get_test_methods()

        # First pass: separate modifiers from regular items
        merged = {}
        modifiers = []  # List of (base_class, modifier) tuples

        for plugin_methods in plugin_test_methods:
            if not plugin_methods:
                continue

            for base_class, methods_dict in plugin_methods.items():
                if base_class not in merged:
                    merged[base_class] = {}

                # Separate modifiers from regular items
                for item_name, item in methods_dict.items():
                    if isinstance(item, BaseModifier):
                        # Collect modifier for later application
                        modifiers.append((base_class, item))
                    else:
                        # Regular item - add/override directly
                        merged[base_class][item_name] = item

        # Second pass: apply all modifiers
        for base_class, modifier in modifiers:
            # Let the modifier apply itself to the mapping
            modifier.apply_to_dict(merged[base_class])

        return merged

    def get_create_data(self) -> dict[str, Any]:
        """Get data for create POST request.

        Creates a temporary object with the factory, converts to dict, then deletes it.
        This ensures all ForeignKey relations are properly saved with PKs.

        Returns:
            Dictionary of form data for POST request
        """
        # Create object (with saved ForeignKeys), convert to dict, then delete
        temp_obj = self.model_factory_class.create(**self.get_factory_kwargs())
        data = self.obj_to_dict(temp_obj)
        temp_obj.delete()
        return data

    def get_update_data(self, obj: models.Model) -> dict[str, Any]:
        """Get data for update POST request.

        Args:
            obj: Model instance being updated

        Returns:
            Dictionary of form data for POST request
        """
        data = self.obj_to_dict(obj)
        data.update(self.to_update_fields)
        return data

    def obj_to_dict(self, obj: models.Model) -> dict[str, Any]:
        """Convert model instance to dict for POST data.

        Handles common field type conversions (Decimal to string, None to empty string, etc.)

        Args:
            obj: Model instance to convert

        Returns:
            Dictionary suitable for form POST data
        """
        from django.forms.models import model_to_dict

        data = model_to_dict(obj, exclude=['id'])

        # Convert values to form-compatible types
        for key, value in list(data.items()):
            if value is None:
                # Django test client can't encode None - use empty string
                data[key] = ''
            elif isinstance(value, Decimal):
                # Convert Decimal to string
                data[key] = str(value)

        return data

    # ========================================
    # Permission Enforcement Testing (Milestone 5 Phase 2.5)
    # ========================================

    def _has_permission_class(self):
        """Check if ModelAdmin has a permission_class set (not None).

        Returns:
            bool: True if permission_class is set and not None
        """
        try:
            model_admin = self._get_model_admin()
            return getattr(model_admin, 'permission_class', None) is not None
        except ValueError:
            # Model not registered yet
            return False

    def _test_requires_authentication(self):
        """Run tests without authentication and verify they fail appropriately.

        This method logs out the current user, attempts to access all action URLs,
        and verifies that access is denied (403 or redirect to login).

        After verification, the user is logged back in for subsequent tests.
        """
        # Logout the user
        self.client.logout()

        # Get all actions and test each one
        actions = self._get_all_actions()

        for action in actions:
            # Get URL for this action
            url = self._get_action_url(action, obj=self.obj if hasattr(self, 'obj') else None)

            # Try to access without authentication - should fail
            response = self.client.get(url, follow=False)

            # Assert that access was denied
            # Accept 302 (redirect to login) or 403 (permission denied)
            assert response.status_code in [302, 403], (
                f'Action {action.__class__.__name__} at {url} should deny '
                f'unauthenticated access, got status {response.status_code}. '
                f"If this is a structure test that doesn't need permissions, "
                f'set permission_class_override=None in your test class.'
            )

        # Re-login for next test
        self.client.force_login(self.user)

    # ========================================
    # Main Test Entry Point
    # ========================================

    def test_actions(self):
        """Introspect all actions and run appropriate tests based on base classes.

        This is the main test method that discovers all actions from the ModelAdmin
        and runs appropriate tests based on plugin-provided test methods.

        NEW in Phase 2.5: When test_permission_enforcement=True, this method
        runs twice:
        1. First with authentication (normal test flow)
        2. Then without authentication (permission enforcement verification)
        """
        # Run authenticated tests
        actions = self._get_all_actions()
        test_methods_mapping = self._get_test_methods_mapping()

        for action in actions:
            # Check each mapped base class
            for base_class, methods_dict in test_methods_mapping.items():
                if isinstance(action, base_class):
                    # Run all test methods for this base class
                    for _, test_method_callable in methods_dict.items():
                        # Run the test with the action
                        # Plugin-provided methods are callables that take (test_case, action)
                        test_method_callable(self, action)

        # Run unauthenticated tests if permission enforcement is enabled
        if self.test_permission_enforcement and self._has_permission_class():
            self._test_requires_authentication()

    # ========================================
    # Customization Hooks
    # ========================================
    # Test methods are provided by plugins via djadmin_get_test_methods hook.
    # See djadmin/plugins/core/djadmin_hooks.py for default implementations.

    def assert_create_successful(self, response, data: dict[str, Any]):
        """Override to add custom assertions after create.

        Args:
            response: HTTP response from POST request
            data: Form data that was posted
        """
        pass

    def assert_update_successful(self, response, obj: models.Model, data: dict[str, Any]):
        """Override to add custom assertions after update.

        Args:
            response: HTTP response from POST request
            obj: Model instance that was updated
            data: Form data that was posted
        """
        pass

    def assert_delete_successful(self, response, obj: models.Model):
        """Override to add custom assertions after delete.

        Args:
            response: HTTP response from POST request
            obj: Model instance that was deleted
        """
        pass
