"""Tests for BaseCRUDTestCase test utility."""

from decimal import Decimal

import pytest
from django.test import override_settings

from djadmin import AdminSite, ModelAdmin, site
from djadmin.testing import BaseCRUDTestCase
from examples.webshop.factories import CategoryFactory, ProductFactory
from examples.webshop.models import Category, Product


# Dynamic URLconf that regenerates URLs on each request
class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestProductCRUD(BaseCRUDTestCase):
    """Test CRUD for Product using BaseCRUDTestCase."""

    model = Product
    model_factory_class = ProductFactory

    # Phase 2.5: We're testing CRUD functionality, not permissions
    # Disable permission enforcement to focus on testing the CRUD helper itself
    test_permission_enforcement = False
    permission_class_override = None

    to_update_fields = {
        'name': 'Updated Product',
        'price': Decimal('199.99'),
    }

    def setUp(self):
        """Set up test data and save registry state."""
        # Save the current Product registrations to restore later
        self._saved_product_registry = list(site._registry.get(Product, []))

        # Clear Product registry for clean test
        if Product in site._registry:
            site.unregister(Product)

        # Register ProductAdmin for testing
        class ProductAdmin(ModelAdmin):
            list_display = ['name', 'sku', 'price']
            permission_class = None  # Disable permissions for CRUD helper testing

        site.register(Product, ProductAdmin, override=True)

        # Create test object via factory
        super().setUp()

    def tearDown(self):
        """Restore registry state after test."""
        from django.urls import clear_url_caches

        # Clear any registrations made during test
        if Product in site._registry:
            site.unregister(Product)

        # Restore original Product registrations (even if empty - restore the saved state)
        site._registry[Product] = list(self._saved_product_registry)

        # Force Django to reload URLs on next request
        clear_url_caches()

        # Also clear the test client's resolver cache
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def assert_create_successful(self, response, data):
        """Verify product was created with correct data."""
        created_product = Product.objects.latest('id')
        assert created_product.name == data['name']
        assert str(created_product.price) == data['price']

    def assert_update_successful(self, response, obj, data):
        """Verify price was updated correctly."""
        assert obj.price == Decimal('199.99')
        assert obj.name == 'Updated Product'


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestCategoryCRUD(BaseCRUDTestCase):
    """Test CRUD for Category using BaseCRUDTestCase."""

    model = Category
    model_factory_class = CategoryFactory

    # Phase 2.5: We're testing CRUD functionality, not permissions
    test_permission_enforcement = False
    permission_class_override = None

    to_update_fields = {
        'name': 'Updated Category',
        'slug': 'updated-category',
    }

    def setUp(self):
        """Set up test data and save registry state."""
        # Save the current Category registrations to restore later
        self._saved_category_registry = list(site._registry.get(Category, []))

        # Clear Category registry for clean test
        if Category in site._registry:
            site.unregister(Category)

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            permission_class = None  # Disable permissions for CRUD helper testing

        site.register(Category, CategoryAdmin, override=True)

        super().setUp()

    def tearDown(self):
        """Restore registry state after test."""
        from django.urls import clear_url_caches

        # Clear any registrations made during test
        if Category in site._registry:
            site.unregister(Category)

        # Restore original Category registrations (even if empty - restore the saved state)
        site._registry[Category] = list(self._saved_category_registry)

        # Force Django to reload URLs on next request
        clear_url_caches()

        # Also clear the test client's resolver cache
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')


@pytest.mark.django_db
class TestBaseCRUDTestCaseFeatures:
    """Test BaseCRUDTestCase features and customization hooks."""

    def test_requires_model_attribute(self):
        """Test that ValueError is raised if model is not set."""

        class TestWithoutModel(BaseCRUDTestCase):
            model_factory_class = ProductFactory

        test_instance = TestWithoutModel()
        with pytest.raises(ValueError, match='model attribute must be set'):
            test_instance.setUp()

    def test_requires_factory_attribute(self):
        """Test that ValueError is raised if factory is not set."""

        class TestWithoutFactory(BaseCRUDTestCase):
            model = Product

        test_instance = TestWithoutFactory()
        with pytest.raises(ValueError, match='model_factory_class attribute must be set'):
            test_instance.setUp()

    def test_custom_factory_kwargs(self):
        """Test factory_default_kwargs customization."""

        class TestWithCustomKwargs(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory
            factory_default_kwargs = {'status': 'draft'}

        test_instance = TestWithCustomKwargs()
        test_instance.setUp()

        assert test_instance.obj.status == 'draft'

    @pytest.mark.skip(
        reason='Uses custom AdminSite not in URLconf - violates testing guideline. '
        'Tests should use global djadmin.site instead (see CLAUDE.md)'
    )
    def test_custom_admin_site(self):
        """Test using custom admin site."""
        custom_site = AdminSite(name='custom')

        class ProductAdmin(ModelAdmin):
            list_display = ['name', 'sku']

        custom_site.register(Product, ProductAdmin)

        class TestWithCustomSite(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory
            admin_site = custom_site

        # setUpClass sets admin_site from class attribute
        TestWithCustomSite.setUpClass()

        assert TestWithCustomSite.admin_site == custom_site

        # Clean up
        custom_site.unregister(Product)

    def test_obj_to_dict_handles_decimals(self):
        """Test obj_to_dict converts Decimals to strings."""

        class TestProductConversion(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory

        test_instance = TestProductConversion()
        test_instance.setUp()

        data = test_instance.obj_to_dict(test_instance.obj)

        # Price should be string, not Decimal
        assert isinstance(data['price'], str)

    def test_get_factory_delete_kwargs_fallback(self):
        """Test that get_factory_delete_kwargs falls back to get_factory_kwargs."""

        class TestDeleteKwargs(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory
            factory_default_kwargs = {'status': 'active'}
            # No factory_delete_kwargs set

        test_instance = TestDeleteKwargs()

        # Should fall back to factory_default_kwargs
        delete_kwargs = test_instance.get_factory_delete_kwargs()
        assert delete_kwargs == {'status': 'active'}

    def test_get_factory_delete_kwargs_custom(self):
        """Test that get_factory_delete_kwargs uses custom kwargs when set."""

        class TestDeleteKwargs(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory
            factory_default_kwargs = {'status': 'active'}
            factory_delete_kwargs = {'status': 'discontinued'}

        test_instance = TestDeleteKwargs()

        delete_kwargs = test_instance.get_factory_delete_kwargs()
        assert delete_kwargs == {'status': 'discontinued'}

    @pytest.mark.skip(
        reason='Uses custom AdminSite not in URLconf - violates testing guideline. '
        'Tests should use global djadmin.site instead (see CLAUDE.md)'
    )
    def test_action_url_resolution(self):
        """Test that _get_action_url() resolves URLs correctly."""
        custom_site = AdminSite(name='custom_admin')

        class ProductAdmin(ModelAdmin):
            list_display = ['name']

        custom_site.register(Product, ProductAdmin)

        class TestURLs(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory
            admin_site = custom_site

        TestURLs.setUpClass()
        test_instance = TestURLs()
        test_instance.setUp()

        # Get actions from the admin
        model_admin = custom_site._registry[Product][0]
        list_action = model_admin.general_actions[0]  # ListViewAction

        # Get URL for list action
        url = test_instance._get_action_url(list_action)
        assert isinstance(url, str)
        assert 'product' in url.lower()

        # Get URL for record action with object
        record_actions = model_admin.record_actions
        if record_actions:
            record_action = record_actions[0]  # First record action (edit or delete)
            url = test_instance._get_action_url(record_action, test_instance.obj)
            assert str(test_instance.obj.pk) in url

        # Clean up
        custom_site.unregister(Product)


@pytest.mark.django_db
class TestTestMethodModifiers:
    """Test Remove and Replace modifiers for test methods."""

    def test_remove_modifier_removes_test_method(self):
        """Test that Remove modifier removes a test method from mapping."""
        from djadmin.actions.view_mixins import CreateViewActionMixin
        from djadmin.plugins.modifiers import Remove

        # Create a test instance to access the method
        class TestModifiers(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory

        test_instance = TestModifiers()

        # Mock plugin that removes a test method
        def mock_plugin_with_remove():
            return {
                CreateViewActionMixin: {
                    '_test_create_get': Remove(CreateViewActionMixin, '_test_create_get'),
                }
            }

        # Patch the plugin manager to return our mock
        from unittest.mock import MagicMock

        from djadmin.plugins import pm

        original_hook = pm.hook.djadmin_get_test_methods
        mock_hook = MagicMock()
        mock_hook.return_value = [
            {
                CreateViewActionMixin: {
                    '_test_create_get': lambda tc, a: None,  # Original method
                    '_test_create_post': lambda tc, a: None,
                }
            },
            mock_plugin_with_remove(),  # Plugin that removes _test_create_get
        ]
        pm.hook.djadmin_get_test_methods = mock_hook

        try:
            # Get the mapping
            mapping = test_instance._get_test_methods_mapping()

            # _test_create_get should be removed
            assert CreateViewActionMixin in mapping
            assert '_test_create_get' not in mapping[CreateViewActionMixin]

            # But _test_create_post should still be there
            assert '_test_create_post' in mapping[CreateViewActionMixin]
        finally:
            # Restore original hook
            pm.hook.djadmin_get_test_methods = original_hook

    def test_replace_modifier_replaces_test_method(self):
        """Test that Replace modifier replaces a test method in mapping."""
        from djadmin.actions.view_mixins import CreateViewActionMixin
        from djadmin.plugins.modifiers import Replace

        class TestModifiers(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory

        test_instance = TestModifiers()

        # Define replacement method
        def replacement_method(test_case, action):
            pass

        # Mock plugin that replaces a test method
        def mock_plugin_with_replace():
            return {
                CreateViewActionMixin: {
                    '_test_create_post': Replace(CreateViewActionMixin, '_test_create_post', replacement_method),
                }
            }

        from unittest.mock import MagicMock

        from djadmin.plugins import pm

        original_hook = pm.hook.djadmin_get_test_methods
        mock_hook = MagicMock()

        # Original method
        def original_method(test_case, action):
            pass

        mock_hook.return_value = [
            {
                CreateViewActionMixin: {
                    '_test_create_post': original_method,
                }
            },
            mock_plugin_with_replace(),  # Plugin that replaces the method
        ]
        pm.hook.djadmin_get_test_methods = mock_hook

        try:
            mapping = test_instance._get_test_methods_mapping()

            # Method should be replaced
            assert CreateViewActionMixin in mapping
            assert '_test_create_post' in mapping[CreateViewActionMixin]
            assert mapping[CreateViewActionMixin]['_test_create_post'] == replacement_method
        finally:
            pm.hook.djadmin_get_test_methods = original_hook

    def test_modifier_repr(self):
        """Test string representation of modifiers."""
        from djadmin.actions.view_mixins import CreateViewActionMixin
        from djadmin.plugins.modifiers import Remove, Replace

        def test_method(tc, a):
            pass

        # Test Remove repr
        remove = Remove(CreateViewActionMixin, '_test_create_post')
        assert repr(remove) == "Remove(CreateViewActionMixin, '_test_create_post')"

        # Test Replace repr
        replace = Replace(CreateViewActionMixin, '_test_create_post', test_method)
        assert repr(replace) == "Replace(CreateViewActionMixin, '_test_create_post', test_method)"

    def test_multiple_plugins_with_modifiers(self):
        """Test that multiple plugins can use modifiers in sequence."""
        from djadmin.actions.view_mixins import CreateViewActionMixin, UpdateViewActionMixin
        from djadmin.plugins.modifiers import Remove, Replace

        class TestModifiers(BaseCRUDTestCase):
            model = Product
            model_factory_class = ProductFactory

        test_instance = TestModifiers()

        def method1(tc, a):
            pass

        def method2(tc, a):
            pass

        def replacement(tc, a):
            pass

        from unittest.mock import MagicMock

        from djadmin.plugins import pm

        original_hook = pm.hook.djadmin_get_test_methods
        mock_hook = MagicMock()
        mock_hook.return_value = [
            # Plugin 1: Provides original methods
            {
                CreateViewActionMixin: {
                    '_test_create_get': method1,
                    '_test_create_post': method1,
                },
                UpdateViewActionMixin: {
                    '_test_update_post': method1,
                },
            },
            # Plugin 2: Replaces one, removes another
            {
                CreateViewActionMixin: {
                    '_test_create_post': Replace(CreateViewActionMixin, '_test_create_post', replacement),
                },
                UpdateViewActionMixin: {
                    '_test_update_post': Remove(UpdateViewActionMixin, '_test_update_post'),
                },
            },
        ]
        pm.hook.djadmin_get_test_methods = mock_hook

        try:
            mapping = test_instance._get_test_methods_mapping()

            # CreateViewActionMixin: _test_create_get unchanged, _test_create_post replaced
            assert mapping[CreateViewActionMixin]['_test_create_get'] == method1
            assert mapping[CreateViewActionMixin]['_test_create_post'] == replacement

            # UpdateViewActionMixin: _test_update_post removed
            assert UpdateViewActionMixin in mapping
            assert '_test_update_post' not in mapping[UpdateViewActionMixin]
        finally:
            pm.hook.djadmin_get_test_methods = original_hook
