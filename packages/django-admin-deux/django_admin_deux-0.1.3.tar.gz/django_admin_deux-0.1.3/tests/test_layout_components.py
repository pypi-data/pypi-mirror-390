"""
Tests for Layout API components (Field, Collection, Fieldset, Row, Layout).

Phase 1, Day 1-2: Layout Components
Target: ~60 tests, 100% coverage on layout.py
"""

import pytest
from django.db import models
from django.forms import EmailInput, NumberInput, PasswordInput, Select, Textarea, TextInput

from djadmin.layout import Collection, Field, Fieldset, Layout, Row


# Test models for Collection tests
class Book(models.Model):
    """Test model for Collection tests."""

    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return self.title


class Author(models.Model):
    """Test model for Collection tests."""

    name = models.CharField(max_length=200)

    class Meta:
        app_label = 'tests'

    def __str__(self):
        return self.name


# =============================================================================
# Field Tests
# =============================================================================


class TestFieldBasics:
    """Test basic Field creation and attributes."""

    def test_field_minimal(self):
        """Test minimal Field creation with just name."""
        field = Field('email')

        assert field.name == 'email'
        assert field.label is None
        assert field.widget is None
        assert field.required is None
        assert field.help_text is None
        assert field.initial is None
        assert field.show_if is None
        assert field.hide_if is None
        assert field.calculate is None
        assert field.css_classes == []
        assert field.attrs == {}
        assert field.extra_kwargs == {}

    def test_field_with_label(self):
        """Test Field with custom label."""
        field = Field('price', label='Unit Price ($)')

        assert field.name == 'price'
        assert field.label == 'Unit Price ($)'

    def test_field_with_required(self):
        """Test Field with required attribute."""
        field = Field('name', required=True)

        assert field.required is True

    def test_field_with_help_text(self):
        """Test Field with help text."""
        field = Field('email', help_text='Enter your email address')

        assert field.help_text == 'Enter your email address'

    def test_field_with_initial(self):
        """Test Field with initial value."""
        field = Field('status', initial='active')

        assert field.initial == 'active'

    def test_field_with_css_classes(self):
        """Test Field with CSS classes."""
        field = Field('first_name', css_classes=['flex-1', 'pr-2'])

        assert field.css_classes == ['flex-1', 'pr-2']

    def test_field_with_attrs(self):
        """Test Field with HTML attributes."""
        field = Field('bio', attrs={'rows': 5, 'cols': 40})

        assert field.attrs == {'rows': 5, 'cols': 40}

    def test_field_with_extra_kwargs(self):
        """Test Field with extra form field kwargs."""
        field = Field('email', extra_kwargs={'max_length': 255})

        assert field.extra_kwargs == {'max_length': 255}


class TestFieldWidgets:
    """Test Field widget handling."""

    def test_field_with_widget_class(self):
        """Test Field with widget class."""
        field = Field('email', widget=EmailInput)

        assert field.widget == EmailInput

    def test_field_with_widget_instance(self):
        """Test Field with widget instance."""
        widget_instance = EmailInput(attrs={'class': 'form-control'})
        field = Field('email', widget=widget_instance)

        assert field.widget == widget_instance

    def test_field_widget_shortcut_textarea(self):
        """Test widget shortcut: textarea."""
        field = Field('bio', widget='textarea')

        assert field.widget == Textarea

    def test_field_widget_shortcut_email(self):
        """Test widget shortcut: email."""
        field = Field('email', widget='email')

        assert field.widget == EmailInput

    def test_field_widget_shortcut_number(self):
        """Test widget shortcut: number."""
        field = Field('age', widget='number')

        assert field.widget == NumberInput

    def test_field_widget_shortcut_password(self):
        """Test widget shortcut: password."""
        field = Field('password', widget='password')

        assert field.widget == PasswordInput

    def test_field_widget_shortcut_select(self):
        """Test widget shortcut: select."""
        field = Field('status', widget='select')

        assert field.widget == Select

    def test_field_widget_shortcut_text(self):
        """Test widget shortcut: text."""
        field = Field('name', widget='text')

        assert field.widget == TextInput

    def test_field_widget_shortcut_textinput(self):
        """Test widget shortcut: textinput (alias for text)."""
        field = Field('name', widget='textinput')

        assert field.widget == TextInput

    def test_field_widget_shortcut_case_insensitive(self):
        """Test widget shortcuts are case-insensitive."""
        field1 = Field('bio', widget='TEXTAREA')
        field2 = Field('bio', widget='TextArea')
        field3 = Field('bio', widget='textarea')

        assert field1.widget == Textarea
        assert field2.widget == Textarea
        assert field3.widget == Textarea

    def test_field_widget_shortcut_unknown(self):
        """Test unknown widget shortcut raises ValueError."""
        with pytest.raises(ValueError, match="Unknown widget shortcut 'unknown'"):
            Field('name', widget='unknown')


class TestFieldAdvancedFeatures:
    """Test Field advanced features (conditional, computed)."""

    def test_field_with_show_if(self):
        """Test Field with show_if conditional."""
        field = Field('weight', show_if=".product_type === 'physical'")

        assert field.show_if == ".product_type === 'physical'"
        assert field.hide_if is None

    def test_field_with_hide_if(self):
        """Test Field with hide_if conditional."""
        field = Field('digital_download', hide_if=".product_type === 'physical'")

        assert field.hide_if == ".product_type === 'physical'"
        assert field.show_if is None

    def test_field_with_calculate(self):
        """Test Field with calculate computed value."""
        field = Field('total', calculate='.price * .quantity')

        assert field.calculate == '.price * .quantity'

    def test_field_show_if_and_hide_if_raises_error(self):
        """Test Field with both show_if and hide_if raises ValueError."""
        with pytest.raises(ValueError, match='cannot have both show_if and hide_if'):
            Field('field', show_if='.condition1', hide_if='.condition2')

    def test_has_advanced_features_with_show_if(self):
        """Test has_advanced_features() returns True with show_if."""
        field = Field('weight', show_if=".product_type === 'physical'")

        assert field.has_advanced_features() is True

    def test_has_advanced_features_with_hide_if(self):
        """Test has_advanced_features() returns True with hide_if."""
        field = Field('digital', hide_if=".product_type === 'physical'")

        assert field.has_advanced_features() is True

    def test_has_advanced_features_with_calculate(self):
        """Test has_advanced_features() returns True with calculate."""
        field = Field('total', calculate='.price * .quantity')

        assert field.has_advanced_features() is True

    def test_has_advanced_features_without_features(self):
        """Test has_advanced_features() returns False without features."""
        field = Field('name')

        assert field.has_advanced_features() is False


# =============================================================================
# Collection Tests
# =============================================================================


class TestCollectionBasics:
    """Test basic Collection creation and attributes."""

    def test_collection_with_fields_list(self):
        """Test Collection with fields list."""
        collection = Collection('books', model=Book, fields=['title', 'isbn'])

        assert collection.name == 'books'
        assert collection.model == Book
        assert collection.fields == ['title', 'isbn']
        assert collection.layout is None

    def test_collection_with_layout(self):
        """Test Collection with layout."""
        layout = Layout(Field('title'), Field('isbn'))
        collection = Collection('books', model=Book, layout=layout)

        assert collection.name == 'books'
        assert collection.model == Book
        assert collection.fields is None
        assert collection.layout == layout

    def test_collection_with_field_objects_in_list(self):
        """Test Collection with Field objects in fields list."""
        collection = Collection('books', model=Book, fields=[Field('title'), 'isbn'])

        assert collection.fields == [Field('title'), 'isbn']

    def test_collection_default_attributes(self):
        """Test Collection default attribute values."""
        collection = Collection('books', model=Book, fields=['title'])

        assert collection.min_siblings == 0
        assert collection.max_siblings == 1000
        assert collection.extra_siblings == 1
        assert collection.is_sortable is False
        assert collection.legend is None
        assert collection.form_class is None

    def test_collection_with_custom_attributes(self):
        """Test Collection with custom attributes."""
        collection = Collection(
            'books',
            model=Book,
            fields=['title'],
            min_siblings=1,
            max_siblings=10,
            extra_siblings=2,
            is_sortable=True,
            legend='Published Books',
        )

        assert collection.min_siblings == 1
        assert collection.max_siblings == 10
        assert collection.extra_siblings == 2
        assert collection.is_sortable is True
        assert collection.legend == 'Published Books'

    def test_collection_both_fields_and_layout_raises_error(self):
        """Test Collection with both fields and layout raises ValueError."""
        layout = Layout(Field('title'))

        with pytest.raises(ValueError, match='cannot specify both fields and layout'):
            Collection('books', model=Book, fields=['title'], layout=layout)

    def test_collection_neither_fields_nor_layout_raises_error(self):
        """Test Collection without fields or layout raises ValueError."""
        with pytest.raises(ValueError, match='must specify either fields or layout'):
            Collection('books', model=Book)


# =============================================================================
# Fieldset Tests
# =============================================================================


class TestFieldsetBasics:
    """Test basic Fieldset creation and attributes."""

    def test_fieldset_with_legend(self):
        """Test Fieldset with named legend."""
        fieldset = Fieldset('Personal Information', Field('name'), Field('email'))

        assert fieldset.legend == 'Personal Information'
        assert len(fieldset.fields) == 2
        assert fieldset.description is None
        assert fieldset.css_classes == []

    def test_fieldset_without_legend(self):
        """Test Fieldset without legend (unnamed)."""
        fieldset = Fieldset(None, Field('name'), Field('email'))

        assert fieldset.legend is None
        assert len(fieldset.fields) == 2

    def test_fieldset_with_description(self):
        """Test Fieldset with description."""
        fieldset = Fieldset(
            'Advanced Options',
            Field('custom_field'),
            description='These fields are for advanced users',
        )

        assert fieldset.description == 'These fields are for advanced users'

    def test_fieldset_with_css_classes(self):
        """Test Fieldset with CSS classes."""
        fieldset = Fieldset('Settings', Field('option'), css_classes=['collapse', 'bordered'])

        assert fieldset.css_classes == ['collapse', 'bordered']

    def test_fieldset_without_fields_raises_error(self):
        """Test Fieldset without fields raises ValueError."""
        with pytest.raises(ValueError, match='must contain at least one field'):
            Fieldset('Empty')

    def test_fieldset_with_mixed_items(self):
        """Test Fieldset with Fields and Rows."""
        fieldset = Fieldset(
            'Contact',
            Field('email'),
            Row(Field('phone'), Field('mobile')),
        )

        assert len(fieldset.fields) == 2
        assert isinstance(fieldset.fields[0], Field)
        assert isinstance(fieldset.fields[1], Row)


# =============================================================================
# Row Tests
# =============================================================================


class TestRowBasics:
    """Test basic Row creation and attributes."""

    def test_row_with_two_fields(self):
        """Test Row with two fields."""
        row = Row(Field('first_name'), Field('last_name'))

        assert len(row.fields) == 2
        assert row.css_classes == []

    def test_row_with_three_fields(self):
        """Test Row with three fields."""
        row = Row(Field('city'), Field('state'), Field('zip'))

        assert len(row.fields) == 3

    def test_row_with_css_classes(self):
        """Test Row with CSS classes."""
        row = Row(Field('first_name'), Field('last_name'), css_classes=['gap-4', 'mb-2'])

        assert row.css_classes == ['gap-4', 'mb-2']

    def test_row_without_fields_raises_error(self):
        """Test Row without fields raises ValueError."""
        with pytest.raises(ValueError, match='must contain at least one field'):
            Row()


# =============================================================================
# Layout Tests
# =============================================================================


class TestLayoutBasics:
    """Test basic Layout creation and attributes."""

    def test_layout_with_fields(self):
        """Test Layout with Field items."""
        layout = Layout(Field('name'), Field('email'))

        assert len(layout.items) == 2
        assert layout.renderer is None
        assert layout.css_classes == []

    def test_layout_with_fieldsets(self):
        """Test Layout with Fieldset items."""
        layout = Layout(
            Fieldset('Personal', Field('name')),
            Fieldset('Contact', Field('email')),
        )

        assert len(layout.items) == 2

    def test_layout_with_custom_renderer(self):
        """Test Layout with custom renderer."""

        class CustomRenderer:
            pass

        layout = Layout(Field('name'), renderer=CustomRenderer)

        assert layout.renderer == CustomRenderer

    def test_layout_with_css_classes(self):
        """Test Layout with CSS classes."""
        layout = Layout(Field('name'), css_classes=['form-horizontal'])

        assert layout.css_classes == ['form-horizontal']

    def test_layout_without_items_raises_error(self):
        """Test Layout without items raises ValueError."""
        with pytest.raises(ValueError, match='must contain at least one item'):
            Layout()

    def test_layout_with_mixed_items(self):
        """Test Layout with mixed item types."""
        layout = Layout(
            Field('name'),
            Fieldset('Contact', Field('email')),
            Row(Field('city'), Field('state')),
        )

        assert len(layout.items) == 3


# =============================================================================
# Layout.get_features() Tests
# =============================================================================


class TestLayoutFeatureDetection:
    """Test Layout.get_features() feature detection."""

    def test_get_features_simple_fields(self):
        """Test get_features() with simple fields."""
        layout = Layout(Field('name'), Field('email'))

        features = layout.get_features()

        assert features == set()

    def test_get_features_with_collection(self):
        """Test get_features() detects collections."""
        layout = Layout(Field('name'), Collection('books', model=Book, fields=['title']))

        features = layout.get_features()

        assert 'collections' in features
        assert 'inlines' in features

    def test_get_features_with_conditional_field(self):
        """Test get_features() detects conditional fields."""
        layout = Layout(
            Field('name'),
            Field('weight', show_if=".product_type === 'physical'"),
        )

        features = layout.get_features()

        assert 'conditional_fields' in features

    def test_get_features_with_computed_field(self):
        """Test get_features() detects computed fields."""
        layout = Layout(
            Field('price'),
            Field('total', calculate='.price * .quantity'),
        )

        features = layout.get_features()

        assert 'computed_fields' in features

    def test_get_features_nested_in_fieldset(self):
        """Test get_features() detects features nested in fieldset."""
        layout = Layout(
            Fieldset(
                'Conditional',
                Field('product_type'),
                Field('weight', show_if=".product_type === 'physical'"),
            )
        )

        features = layout.get_features()

        assert 'conditional_fields' in features

    def test_get_features_nested_in_row(self):
        """Test get_features() detects features nested in row."""
        layout = Layout(
            Row(
                Field('price'),
                Field('total', calculate='.price * .quantity'),
            )
        )

        features = layout.get_features()

        assert 'computed_fields' in features

    def test_get_features_collection_with_nested_layout(self):
        """Test get_features() detects features in collection's nested layout."""
        nested_layout = Layout(
            Field('title'),
            Field('subtitle', show_if=".title !== ''"),
        )
        layout = Layout(
            Field('author'),
            Collection('books', model=Book, layout=nested_layout),
        )

        features = layout.get_features()

        assert 'collections' in features
        assert 'conditional_fields' in features

    def test_get_features_multiple_features(self):
        """Test get_features() detects multiple features."""
        layout = Layout(
            Field('name'),
            Field('weight', show_if=".product_type === 'physical'"),
            Field('total', calculate='.price * .quantity'),
            Collection('books', model=Book, fields=['title']),
        )

        features = layout.get_features()

        assert 'conditional_fields' in features
        assert 'computed_fields' in features
        assert 'collections' in features
        assert 'inlines' in features


# =============================================================================
# Layout.from_fieldsets() Tests (Basic)
# =============================================================================


class TestLayoutFromFieldsetsBasic:
    """Test Layout.from_fieldsets() conversion (basic cases)."""

    def test_from_fieldsets_single_named_fieldset(self):
        """Test conversion of single named fieldset."""
        fieldsets = (('Personal', {'fields': ('name', 'email')}),)

        layout = Layout.from_fieldsets(fieldsets)

        assert len(layout.items) == 1
        assert isinstance(layout.items[0], Fieldset)
        assert layout.items[0].legend == 'Personal'
        assert len(layout.items[0].fields) == 2

    def test_from_fieldsets_unnamed_fieldset(self):
        """Test conversion of unnamed fieldset (legend=None)."""
        fieldsets = ((None, {'fields': ('name', 'email')}),)

        layout = Layout.from_fieldsets(fieldsets)

        assert len(layout.items) == 1
        assert layout.items[0].legend is None

    def test_from_fieldsets_tuple_becomes_row(self):
        """Test tuple in fields becomes Row."""
        fieldsets = (('Personal', {'fields': (('first_name', 'last_name'),)}),)

        layout = Layout.from_fieldsets(fieldsets)

        fieldset = layout.items[0]
        assert len(fieldset.fields) == 1
        assert isinstance(fieldset.fields[0], Row)
        assert len(fieldset.fields[0].fields) == 2

    def test_from_fieldsets_mixed_fields_and_tuples(self):
        """Test mixed strings and tuples in fields."""
        fieldsets = (
            (
                'Personal',
                {
                    'fields': (
                        'name',
                        ('first_name', 'last_name'),
                        'email',
                    )
                },
            ),
        )

        layout = Layout.from_fieldsets(fieldsets)

        fieldset = layout.items[0]
        assert len(fieldset.fields) == 3
        assert isinstance(fieldset.fields[0], Field)
        assert isinstance(fieldset.fields[1], Row)
        assert isinstance(fieldset.fields[2], Field)

    def test_from_fieldsets_with_description(self):
        """Test fieldset with description."""
        fieldsets = (
            (
                'Advanced',
                {
                    'fields': ('option',),
                    'description': 'Advanced settings',
                },
            ),
        )

        layout = Layout.from_fieldsets(fieldsets)

        fieldset = layout.items[0]
        assert fieldset.description == 'Advanced settings'

    def test_from_fieldsets_with_classes(self):
        """Test fieldset with CSS classes."""
        fieldsets = (
            (
                'Settings',
                {
                    'fields': ('option',),
                    'classes': ['collapse'],
                },
            ),
        )

        layout = Layout.from_fieldsets(fieldsets)

        fieldset = layout.items[0]
        assert fieldset.css_classes == ['collapse']

    def test_from_fieldsets_multiple_fieldsets(self):
        """Test conversion of multiple fieldsets."""
        fieldsets = (
            ('Personal', {'fields': ('name',)}),
            ('Contact', {'fields': ('email',)}),
        )

        layout = Layout.from_fieldsets(fieldsets)

        assert len(layout.items) == 2
        assert layout.items[0].legend == 'Personal'
        assert layout.items[1].legend == 'Contact'
