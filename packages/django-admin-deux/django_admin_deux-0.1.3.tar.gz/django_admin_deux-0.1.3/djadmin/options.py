from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import lru_cache
from typing import TYPE_CHECKING, ClassVar, Literal

from django.forms import ModelForm

from djadmin.dataclasses import Column, Filter, Order
from djadmin.plugins.permissions import HasDjangoPermission, IsStaff

if TYPE_CHECKING:
    from djadmin.actions.base import BaseAction
    from djadmin.sites import AdminSite


class ModelAdminMetaclass(type):
    """
    Metaclass that normalizes list_display to Column objects and auto-converts fieldsets to layout.

    This allows ModelAdmin to accept both:
    - Django admin style: ['name', 'sku', callable]
    - Enhanced style: [Column('name'), Column('sku', label='SKU Code')]
    - Mixed style: ['name', Column('sku', label='SKU Code')]

    Additionally normalizes filter/order attributes if filter/ordering plugins are installed:
    - filter=True → Filter()
    - filter=False → None
    - order=True → Order()
    - order=False → Order(enabled=False)

    Auto-converts Django admin fieldsets to Layout API (Milestone 3):
    - Allows seamless migration from Django admin
    - Rejects both fieldsets and layout being specified
    - Marks converted layouts with _layout_source = 'fieldsets'
    """

    def __new__(mcs, name, bases, namespace):
        # Skip base ModelAdmin class to avoid processing its defaults
        if name == 'ModelAdmin':
            return super().__new__(mcs, name, bases, namespace)

        # Normalize permission_class: ensure it's an instance or set default
        mcs._normalize_permission_class(namespace)

        # Validate and convert fieldsets to layout
        mcs._process_fieldsets_to_layout(name, namespace, 'fieldsets', 'layout', '_layout_source')
        mcs._process_fieldsets_to_layout(name, namespace, 'create_fieldsets', 'create_layout', '_create_layout_source')
        mcs._process_fieldsets_to_layout(name, namespace, 'update_fieldsets', 'update_layout', '_update_layout_source')

        # Auto-layout generation is removed - it was interfering with form_class priority
        # Layouts are optional - both core plugin and templates handle missing layouts gracefully

        new_class = super().__new__(mcs, name, bases, namespace)

        # Normalize list_display to Column objects
        if hasattr(new_class, 'list_display'):
            if new_class.list_display:
                # Non-empty list_display: normalize each field to Column
                new_class.list_display = [Column.from_field(field) for field in new_class.list_display]
            elif new_class.list_display == []:
                # Empty list_display: normalize to ['__str__']
                new_class.list_display = [Column('__str__')]

        # Normalize filter/order if djadmin-filters (or compatible plugin) is installed
        mcs._normalize_filter_order(new_class)

        return new_class

    @classmethod
    def _normalize_permission_class(mcs, namespace):
        """
        Normalize permission_class attribute.

        If permission_class is a class (not an instance), instantiate it.
        The default is already set on the ModelAdmin base class.

        Args:
            namespace: Class namespace dict
        """
        if 'permission_class' in namespace:
            perm = namespace['permission_class']
            # If it's a class (not an instance), instantiate it
            if perm is not None and isinstance(perm, type):
                namespace['permission_class'] = perm()

    @classmethod
    def _process_fieldsets_to_layout(mcs, class_name, namespace, fieldsets_attr, layout_attr, source_attr):
        """
        Process fieldsets attribute and convert to layout.

        Validates that both fieldsets and layout are not specified, then
        converts fieldsets to layout if present.

        Args:
            class_name: Name of the class being created
            namespace: Class namespace dict
            fieldsets_attr: Name of the fieldsets attribute (e.g., 'fieldsets', 'create_fieldsets')
            layout_attr: Name of the layout attribute (e.g., 'layout', 'create_layout')
            source_attr: Name of the source marker attribute (e.g., '_layout_source')
        """
        has_fieldsets = fieldsets_attr in namespace
        has_layout = layout_attr in namespace

        if has_fieldsets and has_layout:
            from django.core.exceptions import ImproperlyConfigured

            raise ImproperlyConfigured(
                f"{class_name} cannot specify both '{fieldsets_attr}' and '{layout_attr}'. "
                f"Use either Django admin-style '{fieldsets_attr}' or Layout API '{layout_attr}', not both."
            )

        # Auto-convert fieldsets to layout
        if has_fieldsets:
            from djadmin.layout import Layout

            fieldsets = namespace.pop(fieldsets_attr)
            namespace[layout_attr] = Layout.from_fieldsets(fieldsets)
            namespace[source_attr] = fieldsets_attr

    @classmethod
    def _normalize_filter_order(mcs, new_class):
        """
        Normalize filter and order attributes in Column objects.

        Converts boolean values to proper Filter/Order instances.
        """
        from dataclasses import replace

        if not hasattr(new_class, 'list_display') or not new_class.list_display:
            return

        normalized = []
        for column in new_class.list_display:
            # Normalize filter: bool → Filter/None
            if isinstance(column.filter, bool):
                column = replace(column, filter=Filter() if column.filter else None)

            # Normalize order: bool → Order
            if isinstance(column.order, bool):
                if column.order:
                    column = replace(column, order=Order())
                else:
                    column = replace(column, order=Order(enabled=False))
            elif column.order is None:
                # Default: disable ordering (user must explicitly enable)
                column = replace(column, order=Order(enabled=False))

            normalized.append(column)

        new_class.list_display = normalized

        # Process legacy list_filter / order_fields if present
        mcs._normalize_legacy_attributes(new_class, Filter, Order)

    @classmethod
    def _normalize_legacy_attributes(mcs, new_class, Filter, Order):
        """
        Apply legacy list_filter and order_fields to columns.

        This provides backward compatibility with Django admin-style configuration.
        """
        from dataclasses import replace

        # Apply list_filter to matching columns
        if hasattr(new_class, 'list_filter') and new_class.list_filter:
            for i, col in enumerate(new_class.list_display):
                if isinstance(col.field, str):
                    filter_conf = mcs._parse_list_filter(col.field, new_class.list_filter, Filter)
                    if filter_conf and col.filter is None:
                        new_class.list_display[i] = replace(col, filter=filter_conf)

        # Apply order_fields to matching columns
        if hasattr(new_class, 'order_fields') and new_class.order_fields:
            for i, col in enumerate(new_class.list_display):
                if isinstance(col.field, str) and col.field in new_class.order_fields:
                    if not col.order or not col.order.enabled:
                        new_class.list_display[i] = replace(col, order=Order())

    @staticmethod
    def _parse_list_filter(field_name, list_filter, Filter):
        """
        Parse legacy list_filter configuration for a specific field.

        Supports both simple and tuple-based configurations:
        - 'category' → Filter()
        - ('price', ['gte', 'lte']) → Filter(lookup_expr=['gte', 'lte'])

        Args:
            field_name: The field to look for in list_filter
            list_filter: The list_filter configuration
            Filter: The Filter class to instantiate

        Returns:
            Filter instance or None if field not in list_filter
        """
        for item in list_filter:
            if isinstance(item, tuple):
                # Tuple format: ('field', ['lookup1', 'lookup2'])
                if item[0] == field_name and len(item) > 1:
                    return Filter(lookup_expr=item[1])
            elif item == field_name:
                # Simple format: 'field'
                return Filter()
        return None


class ModelAdmin(metaclass=ModelAdminMetaclass):
    """
    Encapsulates all admin options and functionality for a model.
    """

    # Model to administer (set by register)
    model = None

    # ListView configuration
    list_display: list[str | Callable | Column] | None = None
    general_actions: list[type[BaseAction]] | None = None  # Main entry points (ListView, Add, etc.)
    bulk_actions: list[type[BaseAction]] | None = None  # Multi-record operations
    record_actions: list[type[BaseAction]] | None = None  # Single-record operations
    paginate_by: int = 100
    pagination_class: type | None = None

    # Permission configuration
    # Default: staff users with Django model permissions (matches Django admin behavior)
    # Set to None to disable permission checks
    # Metaclass will instantiate if defined as class instead of instance
    permission_class = IsStaff() & HasDjangoPermission()

    # Form configuration (fallbacks)
    form_class: type[ModelForm] | None = None
    fields: list[str] | Literal['__all__'] = '__all__'

    # CreateView specific
    create_form_class: type[ModelForm] | None = None
    create_fields: list[str] | Literal['__all__'] | None = None
    create_fieldsets: tuple | None = None  # Django admin-style (auto-converted to create_layout)
    create_layout = None  # Layout API (takes precedence over create_fieldsets)
    create_view_class: type | None = None

    # DetailView specific
    update_form_class: type[ModelForm] | None = None
    update_fields: list[str] | Literal['__all__'] | None = None
    update_fieldsets: tuple | None = None  # Django admin-style (auto-converted to update_layout)
    update_layout = None  # Layout API (takes precedence over update_fieldsets)
    detail_view_class: type | None = None

    # ListView override
    list_view_class: type | None = None

    # Feature indicators (Phase 1)
    search_fields: list[str] | None = None
    list_filter: list[str | tuple] | None = None  # Legacy support (normalized to Column.filter)
    order_fields: list[str] | None = None  # Legacy support (normalized to Column.order)
    ordering: list[str] | None = None  # Default ordering (different from order_fields)

    # Feature indicators (Future phases - examples)
    inlines: list[type] | None = None
    inline_sortable: bool = False

    # Feature advertising
    FEATURE_INDICATORS: ClassVar[dict[str, list[str]]] = {
        'search': ['search_fields'],
        'filter': ['list_filter'],
        'ordering': ['ordering'],
        'inlines': ['inlines'],
        'sortable': ['inline_sortable'],
    }

    def __init__(self, model, admin_site: AdminSite):
        self.model = model
        self.admin_site = admin_site

        # Initialize list_display if not set
        if self.list_display is None:
            self.list_display = [Column('__str__')]

        # Process inlines (converts Django-style inlines to Collections)
        self._process_inlines_to_layout()

        # Initialize and instantiate action classes
        self._initialize_actions()

    def _initialize_actions(self):
        """
        Initialize action lists by merging plugin defaults with user overrides.

        If user defines general_actions/bulk_actions/record_actions, those are used.
        Otherwise, get defaults from plugins. All action classes are instantiated.
        """
        from djadmin.plugins import pm

        # Get plugin-provided default actions
        plugin_general_actions = []
        plugin_bulk_actions = []
        plugin_record_actions = []

        for action_list in pm.hook.djadmin_get_default_general_actions():
            if action_list:
                plugin_general_actions.extend(action_list)

        for action_list in pm.hook.djadmin_get_default_bulk_actions():
            if action_list:
                plugin_bulk_actions.extend(action_list)

        for action_list in pm.hook.djadmin_get_default_record_actions():
            if action_list:
                plugin_record_actions.extend(action_list)

        # Use user-defined actions or fall back to plugin defaults
        general_action_classes = self.general_actions if self.general_actions is not None else plugin_general_actions
        bulk_action_classes = self.bulk_actions if self.bulk_actions is not None else plugin_bulk_actions
        record_action_classes = self.record_actions if self.record_actions is not None else plugin_record_actions

        # Instantiate all action classes
        self.general_actions = self._instantiate_actions(general_action_classes)
        self.bulk_actions = self._instantiate_actions(bulk_action_classes)
        self.record_actions = self._instantiate_actions(record_action_classes)

    def _create_auto_layout(self):
        """
        Create a basic layout from model fields when no layout or fieldsets specified.

        This ensures every ModelAdmin has a layout attribute, which is used by
        plugins like djadmin-formset to provide enhanced form rendering.
        """
        from djadmin.layout import Field, Layout

        # Get fields from create_fields, update_fields, fields, or all model fields
        fields = self.create_fields or self.update_fields or self.fields

        if fields == '__all__' or fields is None:
            # Extract all editable model fields for auto-layout
            # Note: auto_created=False filters out:
            #   - Reverse foreign keys (e.g., order_set)
            #   - Reverse M2M relations (e.g., Tag.products)
            # But includes:
            #   - Forward M2M fields (e.g., Product.tags)
            #   - Regular fields (CharField, IntegerField, etc.)
            #   - ForeignKey fields
            field_names = [
                f.name
                for f in self.model._meta.get_fields()
                if not f.auto_created and hasattr(f, 'editable') and f.editable
            ]
        else:
            field_names = list(fields)

        self.layout = Layout(*[Field(name) for name in field_names])
        return self.layout

    def _convert_inline_to_collection(self, inline_class):
        """
        Convert Django-style inline class to Collection component.

        Args:
            inline_class: InlineModelAdmin subclass

        Returns:
            Collection component configured to match inline behavior
        """
        from djadmin.layout import Collection

        # Instantiate inline to access attributes
        inline = inline_class()

        # Determine relation name from model
        if inline.model is None:
            raise ValueError(f'{inline_class.__name__}.model must be set')

        # Find the relation name and FK field by checking model's foreign keys and reverse relations
        relation_name = None
        fk_field_name = None
        for field in inline.model._meta.get_fields():
            if hasattr(field, 'related_model') and field.related_model == self.model:
                # Forward FK from inline model to parent model
                relation_name = field.related_query_name()
                fk_field_name = field.name  # The FK field on the inline model (e.g., 'order' for OrderItem)
                break

        if relation_name is None:
            # Try reverse relation (parent model has FK to inline model)
            for field in self.model._meta.get_fields():
                if hasattr(field, 'related_model') and field.related_model == inline.model:
                    relation_name = field.get_accessor_name()
                    break

        if relation_name is None:
            raise ValueError(
                f'Could not determine relation name for {inline_class.__name__}. '
                f'Model {inline.model.__name__} must have a ForeignKey to {self.model.__name__}'
            )

        # Map inline attributes to Collection parameters
        collection_kwargs = {
            'model': inline.model,
            'extra_siblings': inline.extra,
            'min_siblings': inline.min_num,
            'max_siblings': inline.max_num,
            'display_style': inline_class._display_style,
        }

        # Add fields (auto-detect if not specified)
        if inline.fields:
            collection_kwargs['fields'] = inline.fields
        else:
            # Auto-detect editable fields from model (same as Collection does)
            editable_fields = [
                f.name
                for f in inline.model._meta.get_fields()
                if not f.auto_created and f.editable and not f.primary_key
            ]
            # Exclude the foreign key field pointing to the parent model
            # (Collection handles this automatically)
            if fk_field_name and fk_field_name in editable_fields:
                editable_fields.remove(fk_field_name)
            collection_kwargs['fields'] = editable_fields

        # Add legend (verbose name)
        if inline.verbose_name_plural:
            collection_kwargs['legend'] = inline.verbose_name_plural
        elif inline.verbose_name:
            collection_kwargs['legend'] = inline.verbose_name
        else:
            collection_kwargs['legend'] = inline.model._meta.verbose_name_plural

        return Collection(relation_name, **collection_kwargs)

    def _process_inlines_to_layout(self):
        """
        Convert ModelAdmin.inlines to Collection components in layout.

        Emits deprecation warning and automatically converts Django-style
        inline classes to Collection components appended to the layout.
        """
        if not self.inlines:
            return

        # Emit deprecation warning
        warnings.warn(
            f'{self.__class__.__name__}.inlines is deprecated and will be removed in '
            f'django-admin-deux 2.0. Use Collection components in the layout attribute instead. '
            f'See: https://docs.django-admin-deux.dev/layout-api/collections/',
            DeprecationWarning,
            stacklevel=3,
        )

        # Convert each inline to Collection
        collections = []
        for inline_class in self.inlines:
            try:
                collection = self._convert_inline_to_collection(inline_class)
                collections.append(collection)
            except Exception as e:
                raise ValueError(f'Failed to convert {inline_class.__name__} to Collection: {e}') from e

        # Add collections to layout
        if getattr(self, 'layout', None) is None:
            # If no layout exists, create one with just the collections
            # (auto-layout will have already added fields if needed)
            self._create_auto_layout()

        # Append to existing layout
        # Note: self.layout.items is a tuple, we need to extend it
        self.layout.items = (*self.layout.items, *collections)

    def _instantiate_actions(self, action_classes):
        """
        Instantiate action classes, handling both classes and already-instantiated objects.

        Args:
            action_classes: List of action classes or instances

        Returns:
            List of action instances
        """
        instances = []
        for action in action_classes:
            # Check if already an instance
            if isinstance(action, type):
                # It's a class, instantiate it
                instances.append(action(self.model, self, self.admin_site))
            else:
                # Already an instance, use as-is
                instances.append(action)
        return instances

    def filter_actions(self, actions, request, obj=None):
        """
        Filter actions based on user permissions, with request-level caching.

        Uses the action's check_permission() method to determine if
        the user has permission to execute each action. Results are
        cached per request to avoid redundant permission checks.

        Performance Impact:
            Without caching: Actions filtered multiple times per request
            With caching: Actions filtered once per request/object combination

        Args:
            actions: List of action instances
            request: The HTTP request with user information
            obj: Optional specific object instance for object-level permissions

        Returns:
            List of actions that the user has permission to execute
        """
        if not actions:
            return []

        # Use request identity and object PK as cache key
        # This ensures cache is isolated per request and per object
        cache_key = (id(request), obj.pk if obj else None)

        # Create cached filter function with limited cache size
        @lru_cache(maxsize=128)
        def _cached_filter(key):
            return [action for action in actions if action.check_permission(request, obj=obj)]

        return _cached_filter(cache_key)

    @property
    def requested_features(self) -> set:
        """
        Get set of features requested by checking indicator attributes and column configuration.

        Checks both legacy attributes (list_filter, search_fields, etc.) and
        column-centric configuration (Column.filter, Column.order).

        Also checks Layout API features (collections, conditional_fields, computed_fields).
        """
        features = set()

        # Check legacy indicator attributes
        for feature_name, indicator_attrs in self.FEATURE_INDICATORS.items():
            for attr in indicator_attrs:
                value = getattr(self, attr, None)
                if value:  # Truthy check
                    features.add(feature_name)
                    break

        # Check column-centric configuration (after normalization)
        if hasattr(self, 'list_display') and self.list_display:
            # Map feature to column attribute
            column_features = {
                'filter': 'filter',  # Check Column.filter
                'ordering': 'order',  # Check Column.order (truthy when enabled via Order.__bool__)
            }

            for feature_name, column_attr in column_features.items():
                if any(getattr(col, column_attr, None) for col in self.list_display):
                    features.add(feature_name)

        # Check Layout API features from all layout variants
        for layout_attr in ['layout', 'create_layout', 'update_layout']:
            layout = getattr(self, layout_attr, None)
            if layout:
                # Get features from layout (collections, conditional_fields, computed_fields)
                features.update(layout.get_features())

        return features

    @property
    def opts(self):
        """Shortcut to model._meta"""
        return self.model._meta

    @property
    def list_url_name(self):
        """Get URL name for list view (without namespace)"""
        opts = self.model._meta
        return f'{opts.app_label}_{opts.model_name}_list'
