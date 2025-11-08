"""
Tests for FormBuilder (Day 5 - Milestone 3).

Tests the core form building functionality that creates Django ModelForm classes
from Layout definitions. This is fundamental to making layouts functional.

Test coverage:
- Simple form building
- Widget overrides (class and shortcut)
- Field customizations (label, required, help_text, initial)
- Layout structures (fieldsets, rows)
- Field extraction and iteration
- Integration with ModelForm
"""

from django.forms import ModelForm, NumberInput, Textarea, TextInput

from djadmin.forms import FormBuilder
from djadmin.layout import Field, Fieldset, Layout, Row
from examples.webshop.models import Product


class TestSimpleFormBuilding:
    """Test basic form building from layouts."""

    def test_creates_modelform_from_simple_layout(self):
        """FormBuilder creates a valid ModelForm from a simple layout."""
        layout = Layout(
            Field('name'),
            Field('sku'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        # Should create a ModelForm subclass
        assert issubclass(FormClass, ModelForm)

        # Should have correct model
        assert FormClass._meta.model == Product

        # Should have correct fields
        assert set(FormClass._meta.fields) == {'name', 'sku'}

    def test_creates_instantiable_form(self):
        """Generated form can be instantiated."""
        layout = Layout(Field('name'))

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # Should have the field
        assert 'name' in form.fields

    def test_form_includes_layout_attribute(self):
        """Generated form includes djadmin_layout attribute for template rendering."""
        layout = Layout(Field('name'))

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # Should store layout for templates (no underscore - Django templates don't allow it)
        assert hasattr(form, 'djadmin_layout')
        assert form.djadmin_layout is layout

    def test_uses_custom_base_form(self):
        """FormBuilder uses custom base_form if provided."""

        class CustomModelForm(ModelForm):
            custom_attr = 'custom'

        layout = Layout(Field('name'))

        FormClass = FormBuilder.from_layout(layout, Product, base_form=CustomModelForm)

        # Should inherit from custom base
        assert issubclass(FormClass, CustomModelForm)
        assert hasattr(FormClass, 'custom_attr')

    def test_multiple_fields(self):
        """FormBuilder handles layouts with multiple fields."""
        layout = Layout(
            Field('name'),
            Field('sku'),
            Field('price'),
            Field('description'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        assert FormClass._meta.fields == ['name', 'sku', 'price', 'description']


class TestWidgetOverrides:
    """Test widget customization in forms."""

    def test_widget_override_with_class(self):
        """Field widget can be overridden with a widget class."""
        layout = Layout(
            Field('description', widget=Textarea),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # Should use custom widget
        assert isinstance(form.fields['description'].widget, Textarea)

    def test_widget_override_with_instance(self):
        """Field widget can be overridden with a widget instance."""
        layout = Layout(
            Field('price', widget=NumberInput(attrs={'step': '0.01'})),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # Should use custom widget instance
        assert isinstance(form.fields['price'].widget, NumberInput)
        assert form.fields['price'].widget.attrs['step'] == '0.01'

    def test_widget_shortcut_textarea(self):
        """Field widget can use 'textarea' shortcut."""
        layout = Layout(
            Field('description', widget='textarea'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # Widget should be resolved during Field creation
        # (the Field.__post_init__ resolves shortcuts)
        assert isinstance(form.fields['description'].widget, Textarea)

    def test_widget_shortcut_number(self):
        """Field widget can use 'number' shortcut."""
        layout = Layout(
            Field('price', widget='number'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert isinstance(form.fields['price'].widget, NumberInput)

    def test_widget_shortcut_text(self):
        """Field widget can use 'text' shortcut."""
        layout = Layout(
            Field('name', widget='text'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert isinstance(form.fields['name'].widget, TextInput)


class TestFieldCustomizations:
    """Test field attribute customizations (label, required, help_text, initial)."""

    def test_custom_label(self):
        """Field label can be customized."""
        layout = Layout(
            Field('name', label='Product Name'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['name'].label == 'Product Name'

    def test_custom_required(self):
        """Field required can be set."""
        layout = Layout(
            Field('description', required=True),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['description'].required is True

    def test_custom_help_text(self):
        """Field help_text can be customized."""
        layout = Layout(
            Field('sku', help_text='Enter unique product code'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['sku'].help_text == 'Enter unique product code'

    def test_custom_initial(self):
        """Field initial value can be set."""
        layout = Layout(
            Field('status', initial='draft'),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['status'].initial == 'draft'

    def test_multiple_customizations(self):
        """Multiple field customizations work together."""
        layout = Layout(
            Field(
                'price',
                label='Unit Price',
                required=True,
                help_text='Price in USD',
                widget='number',
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        field = form.fields['price']
        assert field.label == 'Unit Price'
        assert field.required is True
        assert field.help_text == 'Price in USD'
        assert isinstance(field.widget, NumberInput)

    def test_extra_kwargs(self):
        """Field.extra_kwargs are applied to form field."""
        layout = Layout(
            Field('name', extra_kwargs={'max_length': 50}),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        # extra_kwargs should be merged into field config
        assert form.fields['name'].max_length == 50


class TestFieldsetLayouts:
    """Test FormBuilder with Fieldset structures."""

    def test_extracts_fields_from_fieldset(self):
        """Fields inside Fieldsets are extracted correctly."""
        layout = Layout(
            Fieldset(
                'Basic Info',
                Field('name'),
                Field('sku'),
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        assert set(FormClass._meta.fields) == {'name', 'sku'}

    def test_extracts_fields_from_multiple_fieldsets(self):
        """Fields from multiple Fieldsets are extracted."""
        layout = Layout(
            Fieldset('Basic', Field('name')),
            Fieldset('Pricing', Field('price')),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        assert set(FormClass._meta.fields) == {'name', 'price'}

    def test_nested_fieldset_customizations(self):
        """Field customizations work inside Fieldsets."""
        layout = Layout(
            Fieldset(
                'Info',
                Field('name', label='Product Name'),
                Field('description', widget='textarea'),
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['name'].label == 'Product Name'
        assert isinstance(form.fields['description'].widget, Textarea)


class TestRowLayouts:
    """Test FormBuilder with Row structures."""

    def test_extracts_fields_from_row(self):
        """Fields inside Rows are extracted correctly."""
        layout = Layout(
            Row(
                Field('name'),
                Field('sku'),
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        assert set(FormClass._meta.fields) == {'name', 'sku'}

    def test_extracts_fields_from_row_in_fieldset(self):
        """Fields inside Row inside Fieldset are extracted."""
        layout = Layout(
            Fieldset(
                'Product Info',
                Row(
                    Field('name'),
                    Field('sku'),
                ),
                Field('description'),
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)

        assert set(FormClass._meta.fields) == {'name', 'sku', 'description'}

    def test_row_field_customizations(self):
        """Field customizations work inside Rows."""
        layout = Layout(
            Row(
                Field('name', label='Product'),
                Field('sku', label='Code'),
            ),
        )

        FormClass = FormBuilder.from_layout(layout, Product)
        form = FormClass()

        assert form.fields['name'].label == 'Product'
        assert form.fields['sku'].label == 'Code'


class TestFieldExtraction:
    """Test the _extract_field_names helper method."""

    def test_extract_from_simple_layout(self):
        """_extract_field_names returns field names in order."""
        layout = Layout(
            Field('name'),
            Field('sku'),
            Field('price'),
        )

        names = FormBuilder._extract_field_names(layout)

        assert names == ['name', 'sku', 'price']

    def test_extract_from_fieldset(self):
        """_extract_field_names handles Fieldsets."""
        layout = Layout(
            Fieldset(
                'Info',
                Field('name'),
                Field('sku'),
            ),
        )

        names = FormBuilder._extract_field_names(layout)

        assert names == ['name', 'sku']

    def test_extract_from_row(self):
        """_extract_field_names handles Rows."""
        layout = Layout(
            Row(
                Field('name'),
                Field('sku'),
            ),
        )

        names = FormBuilder._extract_field_names(layout)

        assert names == ['name', 'sku']

    def test_extract_from_complex_layout(self):
        """_extract_field_names handles complex nested layouts."""
        layout = Layout(
            Field('name'),
            Fieldset(
                'Details',
                Field('sku'),
                Row(
                    Field('price'),
                    Field('stock_quantity'),
                ),
            ),
            Field('description'),
        )

        names = FormBuilder._extract_field_names(layout)

        assert names == ['name', 'sku', 'price', 'stock_quantity', 'description']


class TestFieldIteration:
    """Test the _iterate_fields helper method."""

    def test_iterate_simple_layout(self):
        """_iterate_fields yields all Field objects."""
        field1 = Field('name')
        field2 = Field('sku')
        layout = Layout(field1, field2)

        fields = list(FormBuilder._iterate_fields(layout))

        assert fields == [field1, field2]

    def test_iterate_fieldset(self):
        """_iterate_fields yields Fields inside Fieldsets."""
        field1 = Field('name')
        field2 = Field('sku')
        layout = Layout(
            Fieldset('Info', field1, field2),
        )

        fields = list(FormBuilder._iterate_fields(layout))

        assert fields == [field1, field2]

    def test_iterate_row(self):
        """_iterate_fields yields Fields inside Rows."""
        field1 = Field('name')
        field2 = Field('sku')
        layout = Layout(
            Row(field1, field2),
        )

        fields = list(FormBuilder._iterate_fields(layout))

        assert fields == [field1, field2]

    def test_iterate_complex_layout(self):
        """_iterate_fields handles complex nested layouts."""
        field1 = Field('name')
        field2 = Field('sku')
        field3 = Field('price')
        field4 = Field('description')

        layout = Layout(
            field1,
            Fieldset(
                'Details',
                field2,
                Row(field3, field4),
            ),
        )

        fields = list(FormBuilder._iterate_fields(layout))

        assert fields == [field1, field2, field3, field4]


class TestBuildFieldConfig:
    """Test the _build_field_config helper method."""

    def test_empty_config_for_minimal_field(self):
        """Minimal Field results in empty config."""
        field = Field('name')

        config = FormBuilder._build_field_config(field)

        # No customizations -> empty config
        assert config == {}

    def test_config_includes_label(self):
        """Config includes label when set."""
        field = Field('name', label='Product Name')

        config = FormBuilder._build_field_config(field)

        assert config['label'] == 'Product Name'

    def test_config_includes_widget(self):
        """Config includes widget when set."""
        field = Field('description', widget=Textarea)

        config = FormBuilder._build_field_config(field)

        assert config['widget'] == Textarea

    def test_config_includes_required(self):
        """Config includes required when set."""
        field = Field('name', required=True)

        config = FormBuilder._build_field_config(field)

        assert config['required'] is True

    def test_config_includes_help_text(self):
        """Config includes help_text when set."""
        field = Field('sku', help_text='Unique code')

        config = FormBuilder._build_field_config(field)

        assert config['help_text'] == 'Unique code'

    def test_config_includes_initial(self):
        """Config includes initial when set."""
        field = Field('status', initial='active')

        config = FormBuilder._build_field_config(field)

        assert config['initial'] == 'active'

    def test_config_includes_extra_kwargs(self):
        """Config includes extra_kwargs."""
        field = Field('name', extra_kwargs={'max_length': 100})

        config = FormBuilder._build_field_config(field)

        assert config['max_length'] == 100

    def test_config_merges_all_attributes(self):
        """Config includes all attributes when set."""
        field = Field(
            'price',
            label='Price',
            widget=NumberInput,
            required=True,
            help_text='In USD',
            initial=0,
            extra_kwargs={'min_value': 0},
        )

        config = FormBuilder._build_field_config(field)

        assert config['label'] == 'Price'
        assert config['widget'] == NumberInput
        assert config['required'] is True
        assert config['help_text'] == 'In USD'
        assert config['initial'] == 0
        assert config['min_value'] == 0
