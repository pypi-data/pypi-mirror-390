"""Tests for metaclasses utilities."""

import threading

from django.test import TestCase

from djadmin.utils.metaclasses import SingletonMeta


class TestSingletonMeta(TestCase):
    """Test the SingletonMeta metaclass."""

    def setUp(self):
        """Clear singleton instances before each test."""
        # Clear all instances to ensure clean state
        SingletonMeta._instances.clear()

    def test_singleton_creates_single_instance(self):
        """Test that only one instance is created."""

        class TestFactory(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 42

        factory1 = TestFactory()
        factory2 = TestFactory()

        # Both variables should reference the same instance
        self.assertIs(factory1, factory2)
        self.assertEqual(factory1.value, 42)
        self.assertEqual(factory2.value, 42)

    def test_singleton_subclasses_have_own_instances(self):
        """Test that subclasses get their own singleton instances."""

        class BaseFactory(metaclass=SingletonMeta):
            def __init__(self):
                self.base_value = 'base'

        class DerivedFactory(BaseFactory):
            def __init__(self):
                super().__init__()
                self.derived_value = 'derived'

        base1 = BaseFactory()
        base2 = BaseFactory()
        derived1 = DerivedFactory()
        derived2 = DerivedFactory()

        # Base instances should be the same
        self.assertIs(base1, base2)

        # Derived instances should be the same
        self.assertIs(derived1, derived2)

        # Base and derived should be different
        self.assertIsNot(base1, derived1)

    def test_singleton_init_called_once(self):
        """Test that __init__ is called only once."""

        init_count = {'count': 0}

        class CountingFactory(metaclass=SingletonMeta):
            def __init__(self):
                init_count['count'] += 1
                self.value = 42

        # Create multiple instances
        factory1 = CountingFactory()
        factory2 = CountingFactory()
        factory3 = CountingFactory()

        # __init__ should be called only once
        self.assertEqual(init_count['count'], 1)
        self.assertIs(factory1, factory2)
        self.assertIs(factory2, factory3)

    def test_singleton_thread_safety(self):
        """Test that singleton is thread-safe."""

        instances = []

        class ThreadFactory(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 42

        def create_instance():
            instances.append(ThreadFactory())

        # Create instances from multiple threads
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All instances should be the same
        first_instance = instances[0]
        for instance in instances[1:]:
            self.assertIs(instance, first_instance)

    def test_singleton_with_args_uses_first_instance(self):
        """Test that arguments are only used for first instantiation."""

        class ConfigurableFactory(metaclass=SingletonMeta):
            def __init__(self, value=None):
                self.value = value if value is not None else 42

        # First instantiation with value=100
        factory1 = ConfigurableFactory(value=100)
        self.assertEqual(factory1.value, 100)

        # Second instantiation with value=200 should return same instance
        factory2 = ConfigurableFactory(value=200)
        self.assertIs(factory1, factory2)
        # Value should still be 100 (from first instantiation)
        self.assertEqual(factory2.value, 100)

    def test_singleton_repr_works(self):
        """Test that repr/str work correctly."""

        class TestFactory(metaclass=SingletonMeta):
            def __repr__(self):
                return '<TestFactory>'

        factory = TestFactory()
        self.assertEqual(repr(factory), '<TestFactory>')
