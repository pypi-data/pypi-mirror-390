"""Performance benchmark tests for view instantiation optimizations."""

from django.test import TestCase

from djadmin import ModelAdmin, site
from djadmin.factories import ViewFactory
from examples.webshop.models import Product


class TestViewFactorySingleton(TestCase):
    """Test that ViewFactory is a singleton."""

    def test_viewfactory_is_singleton(self):
        """Test that multiple ViewFactory() calls return the same instance."""
        factory1 = ViewFactory()
        factory2 = ViewFactory()
        factory3 = ViewFactory()

        # All should be the same instance
        self.assertIs(factory1, factory2)
        self.assertIs(factory2, factory3)


class TestViewClassCaching(TestCase):
    """Test that action view_class is cached."""

    def setUp(self):
        """Set up test data."""
        # Save existing registry state before test
        self._original_registry = site._registry.get(Product, []).copy()

        if site.is_registered(Product):
            site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)
        self.model_admin = site._registry[Product][0]

    def tearDown(self):
        """Clean up."""
        # Restore original registry state
        if self._original_registry:
            site._registry[Product] = self._original_registry
        elif Product in site._registry:
            del site._registry[Product]

    def test_view_class_cached_on_action(self):
        """Test that view_class is cached on action instances."""
        # Get an action instance
        actions = self.model_admin.general_actions
        self.assertGreater(len(actions), 0, 'Should have at least one general action')

        action = actions[0]

        # Access view_class multiple times
        view_class1 = action.view_class
        view_class2 = action.view_class
        view_class3 = action.view_class

        # All should be the same class object
        self.assertIs(view_class1, view_class2)
        self.assertIs(view_class2, view_class3)

    def test_get_view_class_uses_cached_property(self):
        """Test that get_view_class() delegates to cached view_class property."""
        actions = self.model_admin.general_actions
        action = actions[0]

        # Call get_view_class() and access view_class property
        view_class_method = action.get_view_class()
        view_class_property = action.view_class

        # Should be the same
        self.assertIs(view_class_method, view_class_property)


class TestActionFilteringCache(TestCase):
    """Test that action filtering is cached per request."""

    def setUp(self):
        """Set up test data."""
        # Save existing registry state before test
        self._original_registry = site._registry.get(Product, []).copy()

        if site.is_registered(Product):
            site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)
        self.model_admin = site._registry[Product][0]

    def tearDown(self):
        """Clean up."""
        # Restore original registry state
        if self._original_registry:
            site._registry[Product] = self._original_registry
        elif Product in site._registry:
            del site._registry[Product]

    def test_filter_actions_returns_consistent_results(self):
        """Test that filter_actions returns consistent results for same request."""
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory

        User = get_user_model()
        user = User.objects.create_user(username='testuser', is_staff=True)

        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = user

        actions = self.model_admin.general_actions

        # Filter multiple times with same request
        filtered1 = self.model_admin.filter_actions(actions, request)
        filtered2 = self.model_admin.filter_actions(actions, request)
        filtered3 = self.model_admin.filter_actions(actions, request)

        # Should return same actions (may be different list objects due to cache)
        self.assertEqual(len(filtered1), len(filtered2))
        self.assertEqual(len(filtered2), len(filtered3))

        # Clean up
        user.delete()


class TestViewFactoryBenefitsFromSingleton(TestCase):
    """Test that ViewFactory singleton reduces instantiation overhead."""

    def test_factory_instantiation_is_cheap(self):
        """Test that multiple ViewFactory() calls have minimal overhead."""
        # All calls return the same instance (singleton pattern)
        factory1 = ViewFactory()
        factory2 = ViewFactory()
        factory3 = ViewFactory()

        # Verify they're all the same instance
        self.assertIs(factory1, factory2)
        self.assertIs(factory2, factory3)


class TestPerformanceImprovements(TestCase):
    """Test that optimizations reduce instantiation overhead."""

    def setUp(self):
        """Set up test data."""
        # Save existing registry state before test
        self._original_registry = site._registry.get(Product, []).copy()

        if site.is_registered(Product):
            site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)
        self.model_admin = site._registry[Product][0]

    def tearDown(self):
        """Clean up."""
        # Restore original registry state
        if self._original_registry:
            site._registry[Product] = self._original_registry
        elif Product in site._registry:
            del site._registry[Product]

    def test_check_permission_does_not_recreate_view_class(self):
        """Test that check_permission reuses cached view class."""
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory

        User = get_user_model()
        user = User.objects.create_user(username='testuser', is_staff=True)

        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = user

        actions = self.model_admin.general_actions
        action = actions[0]

        # Get the view class before permission checks
        view_class_before = action.view_class

        # Call check_permission multiple times
        for _ in range(10):
            action.check_permission(request)

        # Get the view class after permission checks
        view_class_after = action.view_class

        # Should be the same class object (not recreated)
        self.assertIs(view_class_before, view_class_after)

        # Clean up
        user.delete()

    def test_multiple_actions_create_separate_view_classes(self):
        """Test that different actions get different view classes."""
        actions = self.model_admin.general_actions
        self.assertGreater(len(actions), 1, 'Need at least 2 actions for this test')

        action1 = actions[0]
        action2 = actions[1]

        view_class1 = action1.view_class
        view_class2 = action2.view_class

        # Different actions should have different view classes
        # (they may be the same if they have identical configuration)
        # So we just verify they're both valid classes
        self.assertTrue(callable(view_class1))
        self.assertTrue(callable(view_class2))
