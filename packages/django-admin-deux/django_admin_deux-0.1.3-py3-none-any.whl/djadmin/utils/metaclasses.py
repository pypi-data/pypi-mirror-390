"""Metaclasses for django-admin-deux.

This module provides utility metaclasses for implementing common design patterns.
"""

import threading


class SingletonMeta(type):
    """Metaclass that implements the Singleton design pattern.

    Classes using this metaclass will only have one instance throughout the
    application lifecycle. Subsequent instantiation attempts return the same
    instance.

    This is useful for classes that:
    - Manage shared resources (e.g., plugin managers, registries)
    - Are expensive to instantiate (e.g., factories with complex initialization)
    - Should maintain consistent state across the application

    Thread Safety:
        This implementation is thread-safe using a lock to prevent race conditions
        during instance creation.

    Examples:
        Basic usage::

            class MyFactory(metaclass=SingletonMeta):
                def __init__(self):
                    print("Factory initialized")

            factory1 = MyFactory()  # Prints: "Factory initialized"
            factory2 = MyFactory()  # Returns same instance, no print
            assert factory1 is factory2  # True

        With inheritance::

            class BaseFactory(metaclass=SingletonMeta):
                pass

            class ConcreteFactory(BaseFactory):
                pass

            # Each subclass gets its own singleton instance
            base1 = BaseFactory()
            base2 = BaseFactory()
            concrete1 = ConcreteFactory()
            concrete2 = ConcreteFactory()

            assert base1 is base2  # True
            assert concrete1 is concrete2  # True
            assert base1 is not concrete1  # True - different classes

    Note:
        - Each class (not just the base class) gets its own singleton instance
        - Subclasses of a singleton class are also singletons
        - __init__ is called only once per class, when first instantiated
    """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Control instance creation to ensure singleton behavior.

        Args:
            *args: Positional arguments for __init__
            **kwargs: Keyword arguments for __init__

        Returns:
            The singleton instance of the class
        """
        # Use double-checked locking pattern for performance
        # First check without lock (fast path for subsequent calls)
        if cls not in cls._instances:
            # Acquire lock only if instance doesn't exist yet
            with cls._lock:
                # Check again inside lock (another thread might have created it)
                if cls not in cls._instances:
                    # Create the instance
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance

        return cls._instances[cls]
