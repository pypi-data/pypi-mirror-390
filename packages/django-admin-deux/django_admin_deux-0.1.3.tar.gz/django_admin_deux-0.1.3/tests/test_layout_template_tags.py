"""Tests for djadmin_layout template tags."""

from django import forms
from django.template import Context, Template

from djadmin.layout import Collection, Field, Fieldset, Row
from djadmin.templatetags.djadmin_layout import (
    LAYOUT_COMPONENT_CONFIG,
    get_field,
    render_layout_item,
)
from examples.webshop.models import Product


class TestGetFieldFilter:
    """Tests for the get_field template filter."""

    def test_get_field_returns_bound_field(self):
        """Test that get_field returns the correct BoundField."""

        class TestForm(forms.Form):
            name = forms.CharField()
            email = forms.EmailField()

        form = TestForm()
        bound_field = get_field(form, 'name')

        assert bound_field is not None
        assert bound_field.name == 'name'

    def test_get_field_with_missing_field(self):
        """Test that get_field returns None for missing fields."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        bound_field = get_field(form, 'nonexistent')

        assert bound_field is None

    def test_get_field_with_none_form(self):
        """Test that get_field returns None when form is None."""
        bound_field = get_field(None, 'name')
        assert bound_field is None


class TestRenderLayoutItem:
    """Tests for the render_layout_item inclusion tag."""

    def test_render_field_item(self):
        """Test rendering a Field component."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        field = Field('name')
        context = Context({'form': form})

        result = render_layout_item(context, field)

        assert result['template_name'] == 'djadmin/includes/form_field.html'
        assert 'field_def' in result
        assert 'form_field' in result
        assert result['field_def'] == field

    def test_render_fieldset_item(self):
        """Test rendering a Fieldset component."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        fieldset = Fieldset('Personal', Field('name'))
        context = Context({'form': form})

        result = render_layout_item(context, fieldset)

        assert result['template_name'] == 'djadmin/includes/form_fieldset.html'
        assert 'fieldset' in result
        assert 'form' in result
        assert result['fieldset'] == fieldset

    def test_render_row_item(self):
        """Test rendering a Row component."""

        class TestForm(forms.Form):
            first_name = forms.CharField()
            last_name = forms.CharField()

        form = TestForm()
        row = Row(Field('first_name'), Field('last_name'))
        context = Context({'form': form})

        result = render_layout_item(context, row)

        assert result['template_name'] == 'djadmin/includes/form_row.html'
        assert 'row' in result
        assert 'form' in result
        assert result['row'] == row

    def test_render_collection_item(self):
        """Test rendering a Collection component (shows warning)."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        collection = Collection('books', model=Product, fields=['name', 'sku'])
        context = Context({'form': form})

        result = render_layout_item(context, collection)

        assert result['template_name'] == 'djadmin/includes/form_collection_warning.html'
        assert 'collection' in result
        assert result['collection'] == collection

    def test_render_unknown_item_type(self):
        """Test rendering an unknown component type."""

        class UnknownComponent:
            pass

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        unknown = UnknownComponent()
        context = Context({'form': form})

        result = render_layout_item(context, unknown)

        assert result['template_name'] == 'djadmin/includes/form_unknown_component.html'
        assert 'item' in result
        assert 'item_type' in result
        assert result['item_type'] == 'UnknownComponent'


class TestLayoutComponentConfig:
    """Tests for LAYOUT_COMPONENT_CONFIG mapping."""

    def test_all_components_have_config(self):
        """Test that all layout components have configuration."""
        assert Field in LAYOUT_COMPONENT_CONFIG
        assert Fieldset in LAYOUT_COMPONENT_CONFIG
        assert Row in LAYOUT_COMPONENT_CONFIG
        assert Collection in LAYOUT_COMPONENT_CONFIG

    def test_config_has_required_attributes(self):
        """Test that each config has template_name and context_builder."""
        for _component_type, config in LAYOUT_COMPONENT_CONFIG.items():
            assert hasattr(config, 'template_name')
            assert hasattr(config, 'context_builder')
            assert callable(config.context_builder)

    def test_field_context_builder(self):
        """Test that field context builder creates correct context."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        field = Field('name', label='Full Name')

        config = LAYOUT_COMPONENT_CONFIG[Field]
        context = config.context_builder(field, form)

        assert 'field_def' in context
        assert 'form_field' in context
        assert context['field_def'] == field
        assert context['form_field'].name == 'name'

    def test_fieldset_context_builder(self):
        """Test that fieldset context builder creates correct context."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        fieldset = Fieldset('Personal', Field('name'))

        config = LAYOUT_COMPONENT_CONFIG[Fieldset]
        context = config.context_builder(fieldset, form)

        assert 'fieldset' in context
        assert 'form' in context
        assert context['fieldset'] == fieldset
        assert context['form'] == form


class TestTemplateRendering:
    """Integration tests for template rendering with layout tags."""

    def test_render_layout_item_in_template(self):
        """Test that render_layout_item works in a template."""

        class TestForm(forms.Form):
            name = forms.CharField()

        form = TestForm()
        field = Field('name')

        template = Template('{% load djadmin_layout %}' '{% render_layout_item item %}')
        context = Context({'form': form, 'item': field})
        rendered = template.render(context)

        # Should include the field template
        assert 'form-field' in rendered or 'name' in rendered.lower()

    def test_get_field_in_template(self):
        """Test that get_field filter works in a template."""

        class TestForm(forms.Form):
            name = forms.CharField(label='Full Name')

        form = TestForm()

        template = Template(
            '{% load djadmin_layout %}' '{% with field=form|get_field:"name" %}' '{{ field.label }}' '{% endwith %}'
        )
        context = Context({'form': form})
        rendered = template.render(context)

        assert 'Full Name' in rendered
