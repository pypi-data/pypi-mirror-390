"""Generic modifiers for plugin customization.

This module provides modifier classes that allow plugins to modify behavior
provided by other plugins. This is analogous to djp's Before/After modifiers
for INSTALLED_APPS ordering, but for any plugin-provided functionality.

Modifiers:
    - Remove: Remove an item from a mapping
    - Replace: Replace an item in a mapping with a new implementation

These modifiers can be used in any plugin hook that returns mappings.
For example:
    - Test methods (djadmin_get_test_methods)
    - View mixins (djadmin_get_create_view_mixins, etc.)
    - Actions (future use cases)
    - Any other plugin-provided mappings

Example:
    @hookimpl
    def djadmin_get_test_methods():
        from djadmin.plugins.modifiers import Replace
        from djadmin.actions.view_mixins import CreateViewActionMixin

        def custom_test(test_case, action):
            # Custom implementation
            ...

        return {
            CreateViewActionMixin: {
                # Replace a test method from another plugin
                '_test_create_post': Replace(
                    CreateViewActionMixin,
                    '_test_create_post',
                    custom_test
                )
            }
        }
"""

from typing import Any


class BaseModifier:
    """Base class for modifiers.

    Modifiers know how to apply themselves to a mapping. This follows the
    Open/Closed Principle - new modifier types can be added without changing
    the code that processes them.
    """

    def apply_to_dict(self, mapping: dict) -> None:
        """Apply this modifier to a mapping.

        The modifier uses its own instance attributes (base_class, item_name, etc.)
        to determine what changes to make.

        Args:
            mapping: The mapping to modify (modified in place)
        """
        raise NotImplementedError('Subclasses must implement apply_to_dict()')


class Remove(BaseModifier):
    """Modifier to remove an item from a mapping.

    This allows plugins to disable functionality provided by other plugins
    when that functionality doesn't apply to the plugin's modifications.

    Args:
        base_class: The base class or key (e.g., CreateViewActionMixin)
        item_name: The item name to remove (e.g., '_test_create_post')

    Example - Removing a test method:
        @hookimpl
        def djadmin_get_test_methods():
            from djadmin.actions.view_mixins import UpdateViewActionMixin
            from djadmin.plugins.modifiers import Remove

            # Remove the standard update POST test
            return {
                UpdateViewActionMixin: {
                    '_test_update_post': Remove(
                        UpdateViewActionMixin,
                        '_test_update_post'
                    )
                }
            }

    Example - Removing a view mixin:
        @hookimpl
        def djadmin_get_create_view_mixins():
            from djadmin.plugins.modifiers import Remove

            # Remove a mixin that conflicts with ours
            return {
                'ConflictingMixin': Remove('ConflictingMixin', 'ConflictingMixin')
            }
    """

    def __init__(self, base_class: type | str, item_name: str):
        """Initialize Remove modifier.

        Args:
            base_class: The base class or key
            item_name: The item name to remove
        """
        self.base_class = base_class
        self.item_name = item_name

    def apply_to_dict(self, mapping: dict) -> None:
        """Remove the item from the mapping.

        Args:
            mapping: The mapping to modify
        """
        # Remove the item if it exists (pop with default None doesn't raise KeyError)
        mapping.pop(self.item_name, None)

    def __repr__(self) -> str:
        """String representation for debugging."""
        class_name = self.base_class.__name__ if hasattr(self.base_class, '__name__') else str(self.base_class)
        return f'Remove({class_name}, {self.item_name!r})'


class Replace(BaseModifier):
    """Modifier to replace an item in a mapping.

    This allows plugins to override functionality provided by other plugins
    with custom implementations. The replacement will be used instead of the original.

    Args:
        base_class: The base class or key (e.g., CreateViewActionMixin)
        item_name: The item name to replace (e.g., '_test_create_post')
        new_item: The new item (callable, class, or any value)

    Example - Replacing a test method:
        @hookimpl
        def djadmin_get_test_methods():
            from djadmin.actions.view_mixins import CreateViewActionMixin
            from djadmin.plugins.modifiers import Replace

            def custom_test(test_case, action):
                # Custom FormCollection implementation
                ...

            return {
                CreateViewActionMixin: {
                    # Replace core's test with custom version
                    '_test_create_post': Replace(
                        CreateViewActionMixin,
                        '_test_create_post',
                        custom_test
                    )
                }
            }

    Example - Replacing a view mixin:
        @hookimpl
        def djadmin_get_create_view_mixins():
            from djadmin.plugins.modifiers import Replace

            class CustomMixin:
                def custom_method(self):
                    ...

            return {
                'SomeMixin': Replace('SomeMixin', 'SomeMixin', CustomMixin)
            }
    """

    def __init__(self, base_class: type | str, item_name: str, new_item: Any):
        """Initialize Replace modifier.

        Args:
            base_class: The base class or key
            item_name: The item name to replace
            new_item: The new item (callable, class, or any value)
        """
        self.base_class = base_class
        self.item_name = item_name
        self.new_item = new_item

    def apply_to_dict(self, mapping: dict) -> None:
        """Replace the item in the mapping with the new item.

        Args:
            mapping: The mapping to modify
        """
        # Set the new item, overwriting any existing value
        mapping[self.item_name] = self.new_item

    def __repr__(self) -> str:
        """String representation for debugging."""
        class_name = self.base_class.__name__ if hasattr(self.base_class, '__name__') else str(self.base_class)
        item_name = self.new_item.__name__ if hasattr(self.new_item, '__name__') else str(self.new_item)
        return f'Replace({class_name}, {self.item_name!r}, {item_name})'


# ============================================================================
# INSTALLED_APPS ordering modifiers
# ============================================================================


class First:
    """Place app at the very beginning of the list (first position).

    Apps marked with First() will be loaded before all other apps, including
    those in the "before" bucket. This is primarily used for theme plugins
    that need their templates to take precedence over all others.

    Args:
        app: App name to place first

    Example:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import First

            return [
                First('djadmin.plugins.theme'),  # Theme loads first for template precedence
            ]

    Note:
        If multiple plugins use First(), they will appear in the order they
        are registered (plugin registration order).
    """

    def __init__(self, app: str):
        """Initialize the First modifier.

        Args:
            app: App name to place first
        """
        self.app = app

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'First({self.app!r})'


class Before:
    """Place app in the "before" bucket (loaded before default apps).

    Apps marked with Before() will be loaded before the core djadmin apps.
    This is useful for apps that need to be loaded early (e.g., for templates
    to take precedence).

    Args:
        app: App name to place in the "before" bucket

    Example:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import Before

            return [
                Before('django.contrib.staticfiles'),  # Load staticfiles early
            ]
    """

    def __init__(self, app: str):
        """Initialize the Before modifier.

        Args:
            app: App name to place in the "before" bucket
        """
        self.app = app

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'Before({self.app!r})'


class After:
    """Place app in the "after" bucket (loaded after default apps).

    Apps marked with After() will be loaded after the core djadmin apps.
    This is useful for optional apps that depend on core functionality.

    Args:
        app: App name to place in the "after" bucket

    Example:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import After

            return [
                After('myapp.optional_feature'),  # Load after core apps
            ]
    """

    def __init__(self, app: str):
        """Initialize the After modifier.

        Args:
            app: App name to place in the "after" bucket
        """
        self.app = app

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f'After({self.app!r})'


class Position:
    """Position an app relative to another app.

    Use either `before` or `after`, not both. The positioned app will be
    inserted directly before or after the reference app.

    Args:
        app: App name to position
        before: Place `app` before this app (optional)
        after: Place `app` after this app (optional)

    Raises:
        ValueError: If both `before` and `after` are specified, or if neither is specified

    Example - Place theme before djadmin:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import Position

            return [
                Position('djadmin.plugins.theme', before='djadmin'),
            ]

    Example - Place monitoring after djadmin:
        @hookimpl
        def djadmin_get_required_apps():
            from djadmin.plugins.modifiers import Position

            return [
                Position('djadmin.plugins.monitoring', after='djadmin'),
            ]

    Note:
        This hook only runs if the plugin is registered. For the default theme
        plugin, this only happens when no other plugin provides the 'theme' feature.
    """

    def __init__(self, app: str, before: str | None = None, after: str | None = None):
        """Initialize the Position modifier.

        Args:
            app: App name to position
            before: Place `app` before this app (optional)
            after: Place `app` after this app (optional)

        Raises:
            ValueError: If both `before` and `after` are specified, or if neither is specified
        """
        if before and after:
            raise ValueError('Cannot specify both before and after')

        if not before and not after:
            raise ValueError('Must specify either before or after')

        self.app = app
        self.before = before
        self.after = after

    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.before:
            return f'Position({self.app!r}, before={self.before!r})'
        else:
            return f'Position({self.app!r}, after={self.after!r})'


__all__ = ['Remove', 'Replace', 'First', 'Before', 'After', 'Position']
