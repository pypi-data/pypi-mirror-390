"""
Form building utilities for the Layout API.

Provides the FormBuilder class that creates Django ModelForm classes from Layout definitions.
This is the core piece that makes layouts functional by generating actual forms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.forms import ModelForm

if TYPE_CHECKING:
    from django.db import models

    from djadmin.layout import Field, Layout


class FormBuilder:
    """
    Build Django ModelForm classes from Layout definitions.

    Core implementation that works without plugins. Generates standard ModelForm
    instances with field customizations from the Layout API.

    Example:
        layout = Layout(
            Field('name', label='Product Name'),
            Field('price', widget='number'),
        )

        form_class = FormBuilder.from_layout(layout, Product)
        form = form_class()
    """

    @classmethod
    def create_form(cls, model: type[models.Model], fields) -> type[ModelForm]:
        """
        Create form class from fields (no layout).

        This is used when no layout is provided and we need to generate a form
        from a list of field names.

        Args:
            model: Django model class
            fields: List of field names or '__all__'

        Returns:
            Generated ModelForm class

        Example:
            FormClass = FormBuilder.create_form(Product, fields=['name', 'price'])
            form = FormClass()
        """
        from django.forms import modelform_factory

        return modelform_factory(model, fields=fields)

    @staticmethod
    def from_layout(
        layout: Layout,
        model: type[models.Model],
        base_form: type[ModelForm] | None = None,
    ) -> type[ModelForm]:
        """
        Build a ModelForm class from a Layout definition.

        Creates a standard Django ModelForm with field customizations from the layout.
        The generated form includes:
        - Meta class with model and fields list
        - Field configurations (label, widget, required, help_text, initial)
        - _layout attribute for template rendering

        Args:
            layout: Layout definition with Field components
            model: Django model class
            base_form: Optional base form class (defaults to ModelForm)

        Returns:
            Generated ModelForm class ready for instantiation

        Example:
            layout = Layout(
                Field('name', label='Full Name', required=True),
                Field('bio', widget='textarea'),
            )

            FormClass = FormBuilder.from_layout(layout, Author)
            form = FormClass()
        """
        base = base_form or ModelForm

        # Extract field names from layout
        field_names = FormBuilder._extract_field_names(layout)

        # Build form class attributes
        form_attrs: dict[str, Any] = {
            'djadmin_layout': layout,  # Store for template rendering (no underscore - Django templates don't allow it)
            'Meta': type(
                'Meta',
                (),
                {
                    'model': model,
                    'fields': field_names,
                },
            ),
        }

        # Build field configurations
        field_configs = {}
        for field_def in FormBuilder._iterate_fields(layout):
            config = FormBuilder._build_field_config(field_def)
            if config:
                field_configs[field_def.name] = config

        # Create form class
        form_class = type(
            f'{model.__name__}Form',
            (base,),
            form_attrs,
        )

        # Customize __init__ to apply field configurations
        original_init = form_class.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)

            # Apply field customizations
            for field_name, config in field_configs.items():
                if field_name in self.fields:
                    for attr_name, attr_value in config.items():
                        # Special handling for widget: instantiate if it's a class
                        if attr_name == 'widget' and isinstance(attr_value, type):
                            attr_value = attr_value()
                        setattr(self.fields[field_name], attr_name, attr_value)

        form_class.__init__ = new_init

        return form_class

    @staticmethod
    def _build_field_config(field_def: Field) -> dict[str, Any]:
        """
        Build field configuration dict from Field definition.

        Extracts field attributes (label, widget, required, help_text, initial)
        and any extra_kwargs into a configuration dict.

        Args:
            field_def: Field component from layout

        Returns:
            Dict of field attributes to apply

        Example:
            field = Field('name', label='Full Name', required=True)
            config = _build_field_config(field)
            # Returns: {'label': 'Full Name', 'required': True}
        """
        config: dict[str, Any] = {}

        # Standard field attributes
        if field_def.label is not None:
            config['label'] = field_def.label

        if field_def.widget is not None:
            # Widget can be class, instance, or resolved from shortcut
            config['widget'] = field_def.widget

        if field_def.required is not None:
            config['required'] = field_def.required

        if field_def.help_text is not None:
            config['help_text'] = field_def.help_text

        if field_def.initial is not None:
            config['initial'] = field_def.initial

        # Merge extra_kwargs (allows arbitrary form field kwargs)
        config.update(field_def.extra_kwargs)

        return config

    @staticmethod
    def _extract_field_names(layout: Layout) -> list[str]:
        """
        Extract field names from layout recursively.

        Traverses the layout structure and collects all field names from
        Field components. Handles nested structures (Fieldset, Row).
        Does NOT include Collection fields (those require plugin support).

        Args:
            layout: Layout to extract from

        Returns:
            List of field names in order of appearance

        Example:
            layout = Layout(
                Fieldset('Info',
                    Field('name'),
                    Row(Field('city'), Field('state')),
                ),
            )
            names = _extract_field_names(layout)
            # Returns: ['name', 'city', 'state']
        """
        from djadmin.layout import Field, Fieldset, Row

        names: list[str] = []

        def extract(item):
            """Recursively extract field names."""
            if isinstance(item, Field):
                names.append(item.name)
            elif isinstance(item, Fieldset | Row):
                for field in item.fields:
                    extract(field)
            # Note: Collections are NOT processed here (require plugin)

        for item in layout.items:
            extract(item)

        return names

    @staticmethod
    def _iterate_fields(layout: Layout):
        """
        Iterate all Field objects in layout recursively.

        Generator that yields Field components from the layout structure.
        Handles nested structures (Fieldset, Row).
        Does NOT yield Collection fields (those require plugin support).

        Args:
            layout: Layout to iterate

        Yields:
            Field objects in order of appearance

        Example:
            layout = Layout(
                Field('name'),
                Fieldset('Address',
                    Field('street'),
                    Field('city'),
                ),
            )

            for field in _iterate_fields(layout):
                print(field.name)
            # Prints: name, street, city
        """
        from djadmin.layout import Field, Fieldset, Row

        def iterate(item):
            """Recursively iterate Field objects."""
            if isinstance(item, Field):
                yield item
            elif isinstance(item, Fieldset | Row):
                for field in item.fields:
                    yield from iterate(field)
            # Note: Collections are NOT processed here (require plugin)

        for item in layout.items:
            yield from iterate(item)
