"""Base factory class for view generation"""

from typing import TYPE_CHECKING

from django.views.generic import View

from djadmin.utils.metaclasses import SingletonMeta

if TYPE_CHECKING:
    from djadmin.actions.base import BaseAction


class ViewFactory(metaclass=SingletonMeta):
    """
    Factory for generating Django CBV classes from actions.

    This is the single unified factory that generates views for all
    action types. The factory uses a registry pattern where plugins
    register mixins/attributes/assets for specific action classes.

    Implementation Note:
        ViewFactory is a singleton - only one instance exists throughout
        the application lifecycle. This reduces instantiation overhead
        and ensures consistent behavior across all view creation.

    Example usage:
        from djadmin.actions.list_view import ListViewAction
        from djadmin.factories.base import ViewFactory

        action = ListViewAction(model, model_admin, admin_site)
        factory = ViewFactory()  # Returns singleton instance
        view_class = factory.create_view(action)
    """

    def create_view(self, action: 'BaseAction') -> type[View]:
        """
        Create a view class from an action.

        The action specifies the view type through its mixins (e.g., ListViewActionMixin).
        Plugins can register additional mixins, attributes, and assets based on
        the action's class using isinstance() checks.

        Args:
            action: Action instance with model, model_admin, admin_site

        Returns:
            View class ready to use with .as_view()
        """
        # Get base class from plugins or action
        base_class = self._get_base_class(action)

        # Get mixins from plugins for this action
        mixins = self._get_mixins(action)

        # Build class attributes
        class_dict = self._build_class_dict(action)

        # Generate view class name
        view_name = self._generate_view_name(action)

        # Build MRO: mixins first, then base class
        bases = tuple(mixins) + (base_class,)

        # Create the class
        view_class = type(view_name, bases, class_dict)

        return view_class

    def _get_base_class(self, action: 'BaseAction') -> type[View]:
        """
        Get view base class from plugins or action default.

        Plugins return dictionaries mapping action classes to base classes.
        Factory checks isinstance(action, key) for each key in the registry.

        Args:
            action: Action instance

        Returns:
            View base class
        """
        from djadmin.plugins import pm

        # Get all plugin registries
        results = pm.hook.djadmin_get_action_view_base_class(action=action)

        # Loop through registries and check isinstance
        for registry in results:
            if registry:
                for action_class, base_class in registry.items():
                    if isinstance(action, action_class):
                        return base_class

        # Use action's base_class (from view-type mixin)
        return action.get_base_class()

    def _get_mixins(self, action: 'BaseAction') -> list[type]:
        """
        Get mixin classes from plugins for this action.

        Plugins return dictionaries mapping action classes to lists of mixins.
        Factory checks isinstance(action, key) for each key and collects
        matching mixins.

        Args:
            action: Action instance

        Returns:
            List of mixin classes
        """
        from djadmin.plugins import pm

        # Get all plugin registries
        results = pm.hook.djadmin_get_action_view_mixins(action=action)

        # Collect mixins by checking isinstance
        mixins = []
        for registry in results:
            if registry:
                for action_class, mixin_list in registry.items():
                    if isinstance(action, action_class):
                        if mixin_list:
                            mixins.extend(mixin_list)

        return mixins

    def _get_plugin_attributes(self, action: 'BaseAction') -> dict:
        """
        Get additional class attributes from plugins.

        Plugins return dictionaries mapping action classes to attribute dicts.
        This is the main mechanism for plugins to add view-specific attributes
        like paginate_by, get_queryset, etc.

        Args:
            action: Action instance

        Returns:
            Dict of attribute name -> value pairs
        """
        from djadmin.plugins import pm

        results = pm.hook.djadmin_get_action_view_attributes(action=action)

        attributes = {}
        for registry in results:
            if registry:
                for action_class, attr_dict in registry.items():
                    if isinstance(action, action_class):
                        if attr_dict:
                            # Later plugins/registrations can override earlier ones
                            attributes.update(attr_dict)

        return attributes

    def _get_attribute_bindings(self, action: 'BaseAction') -> list[str]:
        """
        Get attribute names to bind from action to view.

        Plugins return dictionaries mapping action classes to lists of attribute names.
        These attributes will be copied directly from the action instance to the view class.

        Args:
            action: Action instance

        Returns:
            List of attribute names to bind
        """
        from djadmin.plugins import pm

        results = pm.hook.djadmin_get_action_view_attribute_bindings(action=action)

        attribute_names = []
        for registry in results:
            if registry:
                for action_class, attr_list in registry.items():
                    if isinstance(action, action_class):
                        if attr_list:
                            attribute_names.extend(attr_list)

        return attribute_names

    def _get_sidebar_widgets(self, action: 'BaseAction') -> list:
        """
        Get sidebar widgets from plugins for this action.

        Plugins return dictionaries mapping action classes to lists of SidebarWidget instances.
        Factory checks isinstance(action, key) for each key and collects
        matching widgets, sorted by order.

        Args:
            action: Action instance

        Returns:
            List of SidebarWidget instances sorted by order
        """
        from djadmin.plugins import pm

        results = pm.hook.djadmin_get_sidebar_widgets(action=action)

        widgets = []
        for registry in results:
            if registry:
                for action_class, widget_list in registry.items():
                    if isinstance(action, action_class):
                        if widget_list:
                            widgets.extend(widget_list)

        # Sort by order (lower numbers first)
        widgets.sort(key=lambda w: w.order)

        return widgets

    def _get_column_header_icons(self, action: 'BaseAction') -> list:
        """
        Get column header icons from plugins for this action.

        Plugins return dictionaries mapping action classes to lists of ColumnHeaderIcon instances.
        Factory checks isinstance(action, key) for each key and collects
        matching icons, sorted by order.

        Args:
            action: Action instance

        Returns:
            List of ColumnHeaderIcon instances sorted by order
        """
        from djadmin.plugins import pm

        results = pm.hook.djadmin_get_column_header_icons(action=action)

        icons = []
        for registry in results:
            if registry:
                for action_class, icon_list in registry.items():
                    if isinstance(action, action_class):
                        if icon_list:
                            icons.extend(icon_list)

        # Sort by order (lower numbers first)
        icons.sort(key=lambda i: i.order)

        return icons

    def _build_class_dict(self, action: 'BaseAction') -> dict:
        """
        Build the dictionary of class attributes for the view.

        Includes standard attributes (action, model, etc.) and delegates
        to plugins for additional attributes via the registry pattern.

        Args:
            action: Action instance

        Returns:
            Dict of attribute name -> value pairs for the view class
        """
        # Start with base attributes
        class_dict = {
            'action': action,
            'model': action.model,
            'model_admin': action.model_admin,
            'admin_site': action.admin_site,
        }

        # Collect sidebar widgets from plugins
        sidebar_widgets = self._get_sidebar_widgets(action)
        if sidebar_widgets:
            class_dict['sidebar_widgets'] = sidebar_widgets

        # Collect column header icons from plugins
        column_header_icons = self._get_column_header_icons(action)
        if column_header_icons:
            class_dict['column_header_icons'] = column_header_icons

        # Bind attributes from action (methods, properties, etc.)
        for attr_name in self._get_attribute_bindings(action):
            if hasattr(action, attr_name):
                # Get the unbound function from the action's class, not the bound method
                # This allows methods to work correctly when added to the view class
                # Methods that call super() must use super(type(self), self) form
                attr_value = getattr(action.__class__, attr_name, None)
                if attr_value is not None:
                    class_dict[attr_name] = attr_value
                else:
                    # Fallback for instance attributes
                    class_dict[attr_name] = getattr(action, attr_name)

        # Merge in plugin-provided attributes (for computed values, closures, etc.)
        # These override action attributes, allowing plugins to override action methods
        plugin_attributes = self._get_plugin_attributes(action)
        class_dict.update(plugin_attributes)

        return class_dict

    def _generate_view_name(self, action: 'BaseAction') -> str:
        """
        Generate descriptive view class name from action.

        Examples:
            ListViewAction -> ProductListView
            EditRecordAction -> ProductEditRecordView

        Args:
            action: Action instance

        Returns:
            View class name string
        """
        # Handle None model gracefully (for error testing scenarios)
        model_name = action.model.__name__ if action.model else 'Generic'
        action_name = action.__class__.__name__.replace('Action', '')

        # If action_name already ends with 'View', don't add it again
        if action_name.endswith('View'):
            return f'{model_name}{action_name}'
        return f'{model_name}{action_name}View'
