"""
Layout API for form customization.

This module provides a declarative API for defining form layouts with progressive
enhancement. The Layout API works without plugins (basic rendering) but gains
superpowers when the djadmin-formset plugin is installed.

Usage:
    from djadmin import ModelAdmin, Layout, Field, Fieldset, Row, Collection

    class MyModelAdmin(ModelAdmin):
        layout = Layout(
            Fieldset('Personal Information',
                Row(
                    Field('first_name', css_classes=['flex-1']),
                    Field('last_name', css_classes=['flex-1']),
                ),
                Field('birth_date'),
            ),
            Fieldset('Biography',
                Field('bio', widget='textarea'),
            ),
        )
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Union

from django.db import models
from django.forms import Widget


@dataclass
class Field:
    """
    A single form field declaration.

    Part of core djadmin. Works with or without djadmin-formset plugin.

    Examples:
        # Basic
        Field('name')

        # With customization
        Field('price', label='Unit Price ($)', required=True)

        # With widget (supports shortcuts!)
        Field('bio', widget='textarea', attrs={'rows': 5})
        Field('bio', widget=Textarea(attrs={'rows': 5}))  # Also works

        # Conditional visibility (⚠️ requires djadmin-formset plugin!)
        Field('ebook_size', show_if=".format === 'ebook'")

        # Computed values (⚠️ requires djadmin-formset plugin!)
        Field('total', calculate='.price * .quantity')

        # Width control (flexbox)
        Field('first_name', css_classes=['flex-1', 'pr-2'])
    """

    name: str
    label: str | None = None

    # Widget: Can be Widget class, Widget instance, or string shortcut
    widget: type[Widget] | Widget | str | None = None

    required: bool | None = None
    help_text: str | None = None
    initial: Any | None = None

    # ⚠️ Advanced features (require djadmin-formset plugin)
    show_if: str | None = None  # Conditional visibility
    hide_if: str | None = None  # Inverse conditional
    calculate: str | None = None  # Auto-calculated value

    # Styling
    css_classes: list[str] = field(default_factory=list)
    attrs: dict = field(default_factory=dict)

    # Additional form field kwargs
    extra_kwargs: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validation after initialization."""
        if self.show_if and self.hide_if:
            raise ValueError(f"Field '{self.name}' cannot have both show_if and hide_if")

        # Resolve widget shortcuts
        if isinstance(self.widget, str):
            self.widget = self._resolve_widget_shortcut(self.widget)

    @staticmethod
    def _resolve_widget_shortcut(shortcut: str) -> type[Widget]:
        """
        Resolve string widget shortcuts to actual widget classes.

        Supported shortcuts:
        - 'text' / 'textinput' → TextInput
        - 'textarea' → Textarea
        - 'email' → EmailInput
        - 'number' → NumberInput
        - 'password' → PasswordInput
        - 'checkbox' → CheckboxInput
        - 'select' → Select
        - 'radio' → RadioSelect
        - 'date' → DateInput
        - 'datetime' → DateTimeInput
        - 'file' → FileInput
        - 'hidden' → HiddenInput
        """
        from django.forms import (
            CheckboxInput,
            DateInput,
            DateTimeInput,
            EmailInput,
            FileInput,
            HiddenInput,
            NumberInput,
            PasswordInput,
            RadioSelect,
            Select,
            Textarea,
            TextInput,
        )

        shortcuts = {
            'text': TextInput,
            'textinput': TextInput,
            'textarea': Textarea,
            'email': EmailInput,
            'number': NumberInput,
            'password': PasswordInput,
            'checkbox': CheckboxInput,
            'select': Select,
            'radio': RadioSelect,
            'date': DateInput,
            'datetime': DateTimeInput,
            'file': FileInput,
            'hidden': HiddenInput,
        }

        shortcut_lower = shortcut.lower()
        if shortcut_lower not in shortcuts:
            raise ValueError(f"Unknown widget shortcut '{shortcut}'. " f"Supported: {', '.join(shortcuts.keys())}")

        return shortcuts[shortcut_lower]

    def has_advanced_features(self) -> bool:
        """Check if this field uses features requiring djadmin-formset."""
        return bool(self.show_if or self.hide_if or self.calculate)

    def render_for_display(self, obj) -> dict:
        """
        Render field for display (read-only view).

        Args:
            obj: Model instance to get field value from

        Returns:
            Dict with field display data:
            {
                'type': 'field',
                'name': str,
                'label': str,
                'value': Any,
                'css_classes': list,
            }
        """
        # Get field value from object
        value = getattr(obj, self.name, None)

        # Get display label (use custom label or field verbose_name)
        if self.label:
            label = self.label
        else:
            # Try to get verbose_name from model field
            try:
                field = obj._meta.get_field(self.name)
                label = field.verbose_name.title()
            except Exception:
                # Fallback: capitalize field name
                label = self.name.replace('_', ' ').title()

        # Get display value (handle special cases)
        display_value = self._get_display_value(obj, value)

        return {
            'type': 'field',
            'name': self.name,
            'label': label,
            'value': display_value,
            'css_classes': self.css_classes,
        }

    def _get_display_value(self, obj, value):
        """
        Get display-friendly value for field.

        Handles:
        - get_FOO_display() for choices fields
        - Foreign keys (display related object)
        - Many-to-many (list of related objects)
        - Boolean (Yes/No)
        - None (empty string)
        """
        # Try get_FOO_display() method first (for choices)
        display_method = f'get_{self.name}_display'
        if hasattr(obj, display_method):
            return getattr(obj, display_method)()

        # Handle None
        if value is None:
            return ''

        # Handle boolean
        if isinstance(value, bool):
            return 'Yes' if value else 'No'

        # Handle many-to-many (will be a manager)
        if hasattr(value, 'all'):
            # Many-to-many or reverse foreign key
            return ', '.join(str(item) for item in value.all())

        # Default: string representation
        return str(value)


@dataclass
class Collection:
    """
    A collection of related objects (inline editing).

    ⚠️ Requires djadmin-formset plugin to work!
    Without plugin: Will trigger feature advertisement and show helpful error.

    Examples:
        # Simple
        Collection('books', model=Book, fields=['title', 'isbn'])

        # With layout
        Collection('books',
            model=Book,
            layout=Layout(
                Field('title'),
                Row(
                    Field('isbn', css_classes=['flex-1']),
                    Field('format', css_classes=['flex-1']),
                ),
            ),
            is_sortable=True,
        )

        # Nested collections
        Collection('addresses',
            model=Address,
            layout=Layout(
                Field('street'),
                Collection('contacts',  # Nested!
                    model=Contact,
                    fields=['phone', 'email']
                )
            )
        )

        # Display styles (Django admin compatibility)
        Collection('orderitem_set',
            model=OrderItem,
            fields=['product', 'quantity', 'price'],
            display_style='tabular',  # Compact table layout (default)
        )

        Collection('shipping_addresses',
            model=ShippingAddress,
            fields=['street', 'city', 'state', 'zip_code'],
            display_style='stacked',  # Vertical form layout
        )
    """

    name: str
    model: type[models.Model]

    # Either fields list OR layout
    fields: list[Union[str, 'Field']] | None = None
    layout: Optional['Layout'] = None

    # Collection configuration (django-formset FormCollection attributes)
    min_siblings: int = 0
    max_siblings: int = 1000
    extra_siblings: int = 1
    is_sortable: bool = False

    # Display
    legend: str | None = None
    display_style: str = 'tabular'  # 'tabular' or 'stacked'

    # Advanced
    form_class: type | None = None

    def __post_init__(self):
        """Validation."""
        if self.fields and self.layout:
            raise ValueError(f"Collection '{self.name}' cannot specify both fields and layout")
        if not self.fields and not self.layout:
            raise ValueError(f"Collection '{self.name}' must specify either fields or layout")

        # Validate display_style
        if self.display_style not in ('tabular', 'stacked'):
            raise ValueError(f"display_style must be 'tabular' or 'stacked', got {self.display_style!r}")

    def __repr__(self):
        """String representation with non-default values."""
        parts = [f'name={self.name!r}']
        if self.model:
            parts.append(f'model={self.model.__name__}')
        if self.fields:
            parts.append(f'fields={self.fields!r}')
        if self.display_style != 'tabular':
            parts.append(f'display_style={self.display_style!r}')
        return f"Collection({', '.join(parts)})"

    def render_for_display(self, obj) -> dict:
        """
        Render collection for display (related objects).

        Args:
            obj: Model instance to get related objects from

        Returns:
            Dict with collection display data:
            {
                'type': 'collection',
                'name': str,
                'legend': str | None,
                'items': list[dict],  # Each item is rendered layout data
            }
        """
        # Get related manager
        related_manager = getattr(obj, self.name, None)
        if related_manager is None:
            items = []
        elif hasattr(related_manager, 'all'):
            # It's a manager - get all related objects
            related_objects = related_manager.all()
            items = []

            for related_obj in related_objects:
                if self.layout:
                    # Use custom layout
                    item_data = self.layout.render_for_display(related_obj)
                else:
                    # Use fields list
                    item_data = []
                    for field_spec in self.fields:
                        if isinstance(field_spec, str):
                            field = Field(field_spec)
                        else:
                            field = field_spec
                        item_data.append(field.render_for_display(related_obj))

                items.append({'fields': item_data})
        else:
            items = []

        return {
            'type': 'collection',
            'name': self.name,
            'legend': self.legend or self.model._meta.verbose_name_plural.title(),
            'items': items,
        }


@dataclass
class Fieldset:
    """
    Grouping of fields with optional legend (heading).

    Part of core djadmin. Renders as HTML <fieldset> element.

    Examples:
        # Named fieldset
        Fieldset('Personal Information',
            Field('name'),
            Field('birth_date'),
        )

        # Unnamed fieldset (legend=None)
        Fieldset(None,
            Field('name'),
            Field('email'),
        )

        # With description
        Fieldset('Advanced Options',
            Field('custom_field'),
            description='These fields are for advanced users',
            css_classes=['collapse'],
        )
    """

    legend: str | None
    fields: tuple  # Union['Field', 'Collection', 'Row']
    description: str | None = None
    css_classes: list[str] = field(default_factory=list)

    def __init__(
        self,
        legend: str | None,
        *fields,
        description: str | None = None,
        css_classes: list[str] | None = None,
    ):
        self.legend = legend
        self.fields = fields
        self.description = description
        self.css_classes = css_classes or []

        if not fields:
            raise ValueError('Fieldset must contain at least one field')

    def render_for_display(self, obj) -> dict:
        """
        Render fieldset for display.

        Args:
            obj: Model instance to get field values from

        Returns:
            Dict with fieldset display data:
            {
                'type': 'fieldset',
                'legend': str | None,
                'description': str | None,
                'items': list[dict],
                'css_classes': list,
            }
        """
        items = []
        for field_item in self.fields:
            items.append(field_item.render_for_display(obj))

        return {
            'type': 'fieldset',
            'legend': self.legend,
            'description': self.description,
            'items': items,
            'css_classes': self.css_classes,
        }


@dataclass
class Row:
    """
    Horizontal layout of fields using flexbox.

    Part of core djadmin. Renders fields side-by-side.

    Examples:
        # Two columns
        Row(
            Field('first_name', css_classes=['flex-1', 'pr-2']),
            Field('last_name', css_classes=['flex-1', 'pl-2']),
        )

        # Three columns
        Row(
            Field('city', css_classes=['flex-1']),
            Field('state', css_classes=['flex-1']),
            Field('zip', css_classes=['flex-1']),
        )

        # Unequal widths (flexbox basis)
        Row(
            Field('street', css_classes=['flex-[2]']),  # 2/3
            Field('apt', css_classes=['flex-1']),       # 1/3
        )
    """

    fields: tuple  # Union['Field', 'Collection']
    css_classes: list[str] = field(default_factory=list)

    def __init__(self, *fields, css_classes: list[str] | None = None):
        self.fields = fields
        self.css_classes = css_classes or []

        if not fields:
            raise ValueError('Row must contain at least one field')

    def render_for_display(self, obj) -> dict:
        """
        Render row for display (horizontal layout).

        Args:
            obj: Model instance to get field values from

        Returns:
            Dict with row display data:
            {
                'type': 'row',
                'items': list[dict],
                'css_classes': list,
            }
        """
        items = []
        for field_item in self.fields:
            items.append(field_item.render_for_display(obj))

        return {
            'type': 'row',
            'items': items,
            'css_classes': self.css_classes,
        }


@dataclass
class Layout:
    """
    Top-level layout definition for a form.

    Part of core djadmin. Can be used with or without djadmin-formset plugin.

    Examples:
        # Simple (works without plugin)
        Layout(
            Field('name'),
            Field('email'),
        )

        # With fieldsets (works without plugin)
        Layout(
            Fieldset('Personal',
                Field('name'),
                Field('birth_date'),
            ),
        )

        # With collections (⚠️ requires plugin!)
        Layout(
            Field('name'),
            Collection('books', model=Book, fields=['title']),
        )
    """

    items: tuple  # Union['Field', 'Collection', 'Fieldset', 'Row']
    renderer: type | None = None
    css_classes: list[str] = field(default_factory=list)

    def __init__(self, *items, renderer: type | None = None, css_classes: list[str] | None = None):
        self.items = items
        self.renderer = renderer
        self.css_classes = css_classes or []

        if not items:
            raise ValueError('Layout must contain at least one item')

    @classmethod
    def from_fieldsets(cls, fieldsets):
        """
        Convert Django admin fieldsets to Layout.

        Converts the Django admin fieldsets format to the Layout API:
        - Named fieldsets → Fieldset with legend
        - Unnamed fieldsets (None, {...}) → Fieldset with legend=None
        - Tuple syntax ('field1', 'field2') → Row(Field('field1'), Field('field2'))
        - 'classes' → css_classes
        - 'description' → description

        Args:
            fieldsets: Django admin fieldsets tuple format

        Returns:
            Layout instance

        Example:
            # Django admin format
            fieldsets = (
                ('Personal', {
                    'fields': ('name', ('first_name', 'last_name'))
                }),
            )

            # Converts to:
            Layout(
                Fieldset('Personal',
                    Field('name'),
                    Row(
                        Field('first_name'),
                        Field('last_name'),
                    ),
                ),
            )
        """
        layout_items = []

        for fieldset_def in fieldsets:
            # fieldset_def is (legend, options_dict)
            legend, options = fieldset_def

            # Get fields from options
            fields_spec = options.get('fields', ())
            description = options.get('description')
            classes = options.get('classes', [])

            # Convert fields spec to Field/Row objects
            fieldset_items = []
            for field_spec in fields_spec:
                if isinstance(field_spec, tuple):
                    # Tuple means Row
                    row_fields = [Field(name) if isinstance(name, str) else name for name in field_spec]
                    fieldset_items.append(Row(*row_fields))
                elif isinstance(field_spec, str):
                    # String means Field
                    fieldset_items.append(Field(field_spec))
                elif isinstance(field_spec, Field):
                    # Already a Field object
                    fieldset_items.append(field_spec)
                else:
                    raise ValueError(f'Unknown field spec type: {type(field_spec)}')

            # Create Fieldset
            fieldset = Fieldset(legend, *fieldset_items, description=description, css_classes=classes)
            layout_items.append(fieldset)

        return cls(*layout_items)

    def get_features(self) -> set:
        """
        Get the set of features required by this layout.

        Used for feature advertising to plugins.

        Returns:
            Set of feature names:
            - 'collections' / 'inlines': Layout contains Collection components
            - 'conditional_fields': Layout uses show_if/hide_if
            - 'computed_fields': Layout uses calculate
        """
        features = set()

        def check_item(item):
            if isinstance(item, Collection):
                features.add('collections')
                features.add('inlines')  # Alias
                # Recursively check nested layout
                if item.layout:
                    features.update(item.layout.get_features())

            elif isinstance(item, Field):
                if item.show_if or item.hide_if:
                    features.add('conditional_fields')
                if item.calculate:
                    features.add('computed_fields')

            elif isinstance(item, Fieldset | Row):
                for field in item.fields:
                    check_item(field)

            elif isinstance(item, Layout):
                for i in item.items:
                    check_item(i)

        for item in self.items:
            check_item(item)

        return features

    def get_field_names(self) -> list[str]:
        """
        Recursively extract all field names from layout.

        Used to provide Django's ModelForm with the fields list when only
        a layout is specified (no explicit fields attribute).

        Returns:
            List of field names (strings) for use with Django's ModelForm fields attribute.
            Collections are excluded as they represent inline editing, not top-level fields.

        Example:
            >>> layout = Layout(
            ...     Field('name'),
            ...     Fieldset('Details',
            ...         Field('price'),
            ...         Row(Field('sku'), Field('category')),
            ...     ),
            ... )
            >>> layout.get_field_names()
            ['name', 'price', 'sku', 'category']
        """

        def _extract_from_items(items):
            """Recursively extract field names from a collection of items."""
            field_names = []
            for item in items:
                if isinstance(item, Field):
                    field_names.append(item.name)
                elif isinstance(item, Fieldset | Row):
                    field_names.extend(_extract_from_items(item.fields))
                elif isinstance(item, Collection):
                    # Collections are inlines, not top-level fields
                    pass
                elif isinstance(item, Layout):
                    field_names.extend(_extract_from_items(item.items))
            return field_names

        return _extract_from_items(self.items)

    def render_for_display(self, obj) -> list:
        """
        Render layout for display (top-level).

        Args:
            obj: Model instance to get field values from

        Returns:
            List of rendered layout items (each is a dict)
        """
        items = []
        for item in self.items:
            items.append(item.render_for_display(obj))

        return items
