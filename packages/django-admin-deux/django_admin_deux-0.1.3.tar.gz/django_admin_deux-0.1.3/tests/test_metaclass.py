"""
Tests for ModelAdminMetaclass auto-conversion of fieldsets to layout.

Tests the Milestone 3 feature that allows seamless migration from Django admin
by automatically converting fieldsets configuration to Layout API.
"""

import pytest
from django.core.exceptions import ImproperlyConfigured

from djadmin import ModelAdmin
from djadmin.layout import Field, Fieldset, Layout, Row


class TestMetaclassFieldsetsConversion:
    """Test automatic conversion of fieldsets to layout."""

    def test_auto_converts_simple_fieldset(self):
        """Test that a simple fieldset is auto-converted to Layout."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (('Basic Information', {'fields': ('name', 'sku', 'price')}),)

        # Should have layout attribute
        assert hasattr(ProductAdmin, 'layout')
        assert isinstance(ProductAdmin.layout, Layout)

        # Should have _layout_source marker
        assert hasattr(ProductAdmin, '_layout_source')
        assert ProductAdmin._layout_source == 'fieldsets'

        # Should NOT have fieldsets anymore (popped from namespace)
        assert not hasattr(ProductAdmin, 'fieldsets')

        # Check layout structure
        assert len(ProductAdmin.layout.items) == 1
        assert isinstance(ProductAdmin.layout.items[0], Fieldset)
        assert ProductAdmin.layout.items[0].legend == 'Basic Information'
        assert len(ProductAdmin.layout.items[0].fields) == 3

    def test_auto_converts_multiple_fieldsets(self):
        """Test conversion of multiple fieldsets."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (
                ('Basic Information', {'fields': ('name', 'sku')}),
                ('Pricing', {'fields': ('price', 'cost')}),
            )

        assert isinstance(ProductAdmin.layout, Layout)
        assert len(ProductAdmin.layout.items) == 2

        # Check first fieldset
        assert isinstance(ProductAdmin.layout.items[0], Fieldset)
        assert ProductAdmin.layout.items[0].legend == 'Basic Information'

        # Check second fieldset
        assert isinstance(ProductAdmin.layout.items[1], Fieldset)
        assert ProductAdmin.layout.items[1].legend == 'Pricing'

    def test_auto_converts_unnamed_fieldset(self):
        """Test conversion of unnamed fieldset (legend=None)."""

        class ProductAdmin(ModelAdmin):
            fieldsets = ((None, {'fields': ('name', 'sku')}),)

        assert isinstance(ProductAdmin.layout, Layout)
        assert len(ProductAdmin.layout.items) == 1
        assert isinstance(ProductAdmin.layout.items[0], Fieldset)
        assert ProductAdmin.layout.items[0].legend is None

    def test_auto_converts_tuple_syntax_to_row(self):
        """Test that tuple syntax in fields is converted to Row."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (
                (
                    'Information',
                    {
                        'fields': (
                            'name',
                            ('sku', 'price'),  # Tuple should become Row
                        )
                    },
                ),
            )

        assert isinstance(ProductAdmin.layout, Layout)
        fieldset = ProductAdmin.layout.items[0]

        # First field should be a Field
        assert isinstance(fieldset.fields[0], Field)
        assert fieldset.fields[0].name == 'name'

        # Second should be a Row
        assert isinstance(fieldset.fields[1], Row)
        assert len(fieldset.fields[1].fields) == 2
        assert fieldset.fields[1].fields[0].name == 'sku'
        assert fieldset.fields[1].fields[1].name == 'price'

    def test_preserves_description_from_fieldsets(self):
        """Test that description is preserved during conversion."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (('Advanced', {'fields': ('name',), 'description': 'Advanced settings for power users'}),)

        fieldset = ProductAdmin.layout.items[0]
        assert fieldset.description == 'Advanced settings for power users'

    def test_preserves_classes_from_fieldsets(self):
        """Test that CSS classes are preserved during conversion."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (('Collapsible', {'fields': ('name',), 'classes': ['collapse', 'wide']}),)

        fieldset = ProductAdmin.layout.items[0]
        assert 'collapse' in fieldset.css_classes
        assert 'wide' in fieldset.css_classes


class TestMetaclassValidation:
    """Test validation rules in metaclass."""

    def test_rejects_both_fieldsets_and_layout(self):
        """Test that specifying both fieldsets and layout raises error."""

        with pytest.raises(ImproperlyConfigured) as exc_info:

            class ProductAdmin(ModelAdmin):
                fieldsets = (('Info', {'fields': ('name',)}),)
                layout = Layout(Field('name'))

        assert "cannot specify both 'fieldsets' and 'layout'" in str(exc_info.value)
        assert 'ProductAdmin' in str(exc_info.value)

    def test_allows_explicit_layout(self):
        """Test that explicit layout attribute is preserved."""

        custom_layout = Layout(
            Field('name'),
            Field('price'),
        )

        class ProductAdmin(ModelAdmin):
            layout = custom_layout

        # Should preserve the exact layout instance
        assert ProductAdmin.layout is custom_layout

        # Should NOT have _layout_source (not converted)
        assert not hasattr(ProductAdmin, '_layout_source')

    def test_base_modeladmin_not_processed(self):
        """Test that base ModelAdmin class skips metaclass processing."""

        # Base ModelAdmin should not be processed
        assert not hasattr(ModelAdmin, 'layout')
        assert not hasattr(ModelAdmin, '_layout_source')

        # But subclasses should be processed if they have fieldsets
        class ProductAdmin(ModelAdmin):
            fieldsets = (('Info', {'fields': ('name',)}),)

        assert hasattr(ProductAdmin, 'layout')


class TestMetaclassEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_fieldsets_raises_error(self):
        """Test that empty fieldsets raises ValueError."""

        # Empty fieldsets should raise error because Layout requires at least one item
        with pytest.raises(ValueError) as exc_info:

            class ProductAdmin(ModelAdmin):
                fieldsets = ()

        assert 'Layout must contain at least one item' in str(exc_info.value)

    def test_fieldset_with_field_objects(self):
        """Test that Field objects in fields list are preserved."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (
                (
                    'Info',
                    {
                        'fields': (
                            Field('name', label='Product Name'),
                            'sku',
                        )
                    },
                ),
            )

        fieldset = ProductAdmin.layout.items[0]

        # First should be the Field object
        assert isinstance(fieldset.fields[0], Field)
        assert fieldset.fields[0].name == 'name'
        assert fieldset.fields[0].label == 'Product Name'

        # Second should be converted string
        assert isinstance(fieldset.fields[1], Field)
        assert fieldset.fields[1].name == 'sku'

    def test_nested_tuples_converted_to_rows(self):
        """Test that nested tuples are converted to nested Rows."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (
                (
                    'Info',
                    {
                        'fields': (
                            ('name', 'sku'),
                            ('price', 'cost'),
                        )
                    },
                ),
            )

        fieldset = ProductAdmin.layout.items[0]

        # Both should be Rows
        assert isinstance(fieldset.fields[0], Row)
        assert isinstance(fieldset.fields[1], Row)

        # Each Row should have 2 fields
        assert len(fieldset.fields[0].fields) == 2
        assert len(fieldset.fields[1].fields) == 2

    def test_layout_source_marker_only_for_converted(self):
        """Test that _layout_source is only set for converted fieldsets."""

        # Converted from fieldsets
        class ProductAdmin1(ModelAdmin):
            fieldsets = (('Info', {'fields': ('name',)}),)

        assert ProductAdmin1._layout_source == 'fieldsets'

        # Explicit layout
        class ProductAdmin2(ModelAdmin):
            layout = Layout(Field('name'))

        assert not hasattr(ProductAdmin2, '_layout_source')

        # No layout at all
        class ProductAdmin3(ModelAdmin):
            pass

        assert not hasattr(ProductAdmin3, '_layout_source')


class TestMetaclassIntegrationWithOtherNormalization:
    """Test that fieldsets conversion works with other metaclass features."""

    def test_fieldsets_and_list_display_both_work(self):
        """Test that fieldsets conversion doesn't break list_display normalization."""

        class ProductAdmin(ModelAdmin):
            list_display = ['name', 'sku', 'price']
            fieldsets = (('Info', {'fields': ('name', 'description')}),)

        # list_display should still be normalized to Column objects
        from djadmin.dataclasses import Column

        assert all(isinstance(col, Column) for col in ProductAdmin.list_display)

        # layout should be converted from fieldsets
        assert hasattr(ProductAdmin, 'layout')
        assert isinstance(ProductAdmin.layout, Layout)


class TestMetaclassCreateUpdateFieldsets:
    """Test create_fieldsets and update_fieldsets conversion."""

    def test_auto_converts_create_fieldsets(self):
        """Test that create_fieldsets is auto-converted to create_layout."""

        class ProductAdmin(ModelAdmin):
            create_fieldsets = (('Basic Information', {'fields': ('name', 'sku', 'price')}),)

        # Should have create_layout attribute
        assert hasattr(ProductAdmin, 'create_layout')
        assert isinstance(ProductAdmin.create_layout, Layout)

        # Should have _create_layout_source marker
        assert hasattr(ProductAdmin, '_create_layout_source')
        assert ProductAdmin._create_layout_source == 'create_fieldsets'

        # create_fieldsets should be None (inherited from base, but value was popped)
        assert ProductAdmin.create_fieldsets is None

        # Check create_layout structure
        assert len(ProductAdmin.create_layout.items) == 1
        assert isinstance(ProductAdmin.create_layout.items[0], Fieldset)
        assert ProductAdmin.create_layout.items[0].legend == 'Basic Information'

    def test_auto_converts_update_fieldsets(self):
        """Test that update_fieldsets is auto-converted to update_layout."""

        class ProductAdmin(ModelAdmin):
            update_fieldsets = (('Update Information', {'fields': ('name', 'updated_at')}),)

        # Should have update_layout attribute
        assert hasattr(ProductAdmin, 'update_layout')
        assert isinstance(ProductAdmin.update_layout, Layout)

        # Should have _update_layout_source marker
        assert hasattr(ProductAdmin, '_update_layout_source')
        assert ProductAdmin._update_layout_source == 'update_fieldsets'

        # update_fieldsets should be None (inherited from base, but value was popped)
        assert ProductAdmin.update_fieldsets is None

    def test_rejects_both_create_fieldsets_and_create_layout(self):
        """Test that specifying both create_fieldsets and create_layout raises error."""

        with pytest.raises(ImproperlyConfigured) as exc_info:

            class ProductAdmin(ModelAdmin):
                create_fieldsets = (('Info', {'fields': ('name',)}),)
                create_layout = Layout(Field('name'))

        assert "cannot specify both 'create_fieldsets' and 'create_layout'" in str(exc_info.value)

    def test_rejects_both_update_fieldsets_and_update_layout(self):
        """Test that specifying both update_fieldsets and update_layout raises error."""

        with pytest.raises(ImproperlyConfigured) as exc_info:

            class ProductAdmin(ModelAdmin):
                update_fieldsets = (('Info', {'fields': ('name',)}),)
                update_layout = Layout(Field('name'))

        assert "cannot specify both 'update_fieldsets' and 'update_layout'" in str(exc_info.value)

    def test_allows_explicit_create_layout(self):
        """Test that explicit create_layout attribute is preserved."""

        custom_layout = Layout(Field('name'), Field('price'))

        class ProductAdmin(ModelAdmin):
            create_layout = custom_layout

        # Should preserve the exact layout instance
        assert ProductAdmin.create_layout is custom_layout

        # Should NOT have _create_layout_source (not converted)
        assert not hasattr(ProductAdmin, '_create_layout_source')

    def test_allows_explicit_update_layout(self):
        """Test that explicit update_layout attribute is preserved."""

        custom_layout = Layout(Field('name'), Field('updated_at'))

        class ProductAdmin(ModelAdmin):
            update_layout = custom_layout

        # Should preserve the exact layout instance
        assert ProductAdmin.update_layout is custom_layout

        # Should NOT have _update_layout_source (not converted)
        assert not hasattr(ProductAdmin, '_update_layout_source')

    def test_all_fieldsets_variants_can_coexist(self):
        """Test that fieldsets, create_fieldsets, and update_fieldsets can all be used together."""

        class ProductAdmin(ModelAdmin):
            fieldsets = (('General', {'fields': ('name', 'description')}),)
            create_fieldsets = (('Create Info', {'fields': ('name',)}),)
            update_fieldsets = (('Update Info', {'fields': ('name', 'updated_at')}),)

        # All should be converted to their respective layouts
        assert hasattr(ProductAdmin, 'layout')
        assert hasattr(ProductAdmin, 'create_layout')
        assert hasattr(ProductAdmin, 'update_layout')

        # Fieldsets attributes should be removed or None after conversion
        # - fieldsets: doesn't exist in base class, so removed entirely
        # - create_fieldsets/update_fieldsets: defined in base class, so exist but are None
        assert not hasattr(ProductAdmin, 'fieldsets')
        assert ProductAdmin.create_fieldsets is None
        assert ProductAdmin.update_fieldsets is None

        # All should have their source markers
        assert ProductAdmin._layout_source == 'fieldsets'
        assert ProductAdmin._create_layout_source == 'create_fieldsets'
        assert ProductAdmin._update_layout_source == 'update_fieldsets'

    def test_fieldsets_with_create_layout_explicit(self):
        """Test that you can mix fieldsets (converted) with explicit create_layout."""

        custom_create_layout = Layout(Field('name'))

        class ProductAdmin(ModelAdmin):
            fieldsets = (('General', {'fields': ('name', 'description')}),)
            create_layout = custom_create_layout

        # fieldsets should be converted to layout
        assert hasattr(ProductAdmin, 'layout')
        assert ProductAdmin._layout_source == 'fieldsets'

        # create_layout should be preserved as-is
        assert ProductAdmin.create_layout is custom_create_layout
        assert not hasattr(ProductAdmin, '_create_layout_source')
