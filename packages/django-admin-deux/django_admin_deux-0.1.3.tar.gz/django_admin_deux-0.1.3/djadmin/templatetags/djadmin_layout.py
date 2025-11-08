"""Template tags for djadmin layout rendering."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from django import template

from djadmin.layout import Collection, Field, Fieldset, Row

register = template.Library()


@dataclass
class LayoutComponentConfig:
    """Configuration for rendering a layout component.

    Attributes:
        template_name: Path to the template to include
        context_builder: Callable that builds template context from the item
    """

    template_name: str
    context_builder: Callable[[Any, Any], dict[str, Any]]


def _build_field_context(item: Field, form) -> dict[str, Any]:
    """Build context for rendering a Field component."""
    form_field = form[item.name] if form else None
    return {
        'field_def': item,
        'form_field': form_field,
    }


def _build_fieldset_context(item: Fieldset, form) -> dict[str, Any]:
    """Build context for rendering a Fieldset component."""
    return {
        'fieldset': item,
        'form': form,
    }


def _build_row_context(item: Row, form) -> dict[str, Any]:
    """Build context for rendering a Row component."""
    return {
        'row': item,
        'form': form,
    }


def _build_collection_context(item: Collection, form) -> dict[str, Any]:
    """Build context for rendering a Collection component (warning)."""
    return {
        'collection': item,
    }


# Data-driven mapping: component type -> rendering configuration
LAYOUT_COMPONENT_CONFIG: dict[type, LayoutComponentConfig] = {
    Field: LayoutComponentConfig(
        template_name='djadmin/includes/form_field.html',
        context_builder=_build_field_context,
    ),
    Fieldset: LayoutComponentConfig(
        template_name='djadmin/includes/form_fieldset.html',
        context_builder=_build_fieldset_context,
    ),
    Row: LayoutComponentConfig(
        template_name='djadmin/includes/form_row.html',
        context_builder=_build_row_context,
    ),
    Collection: LayoutComponentConfig(
        template_name='djadmin/includes/form_collection_warning.html',
        context_builder=_build_collection_context,
    ),
}


@register.inclusion_tag('djadmin/includes/layout_item.html', takes_context=True)
def render_layout_item(context, item):
    """Render a layout item using the appropriate template.

    Uses data-driven mapping to determine which template to include
    and what context to pass.

    Args:
        context: Template context
        item: Layout component (Field, Fieldset, Row, or Collection)

    Returns:
        dict: Context for rendering the item

    Example:
        {% load djadmin_layout %}
        {% for item in layout.items %}
            {% render_layout_item item %}
        {% endfor %}
    """
    form = context.get('form')

    # Look up configuration for this component type
    config = None
    for component_type, component_config in LAYOUT_COMPONENT_CONFIG.items():
        if isinstance(item, component_type):
            config = component_config
            break

    if not config:
        # Unknown component type - this shouldn't happen but handle gracefully
        return {
            'template_name': 'djadmin/includes/form_unknown_component.html',
            'item': item,
            'item_type': type(item).__name__,
        }

    # Build context using the component's context builder
    item_context = config.context_builder(item, form)

    # Flatten the item_context into the top-level context along with template_name
    result = {'template_name': config.template_name}
    result.update(item_context)

    return result


@register.filter
def get_field(form, field_name):
    """Get a form field by name.

    Args:
        form: Django form instance
        field_name: Name of the field to retrieve

    Returns:
        BoundField: The form field or None if not found

    Example:
        {% with form_field=form|get_field:field_def.name %}
            {{ form_field.label_tag }}
            {{ form_field }}
        {% endwith %}
    """
    if not form:
        return None

    try:
        return form[field_name]
    except KeyError:
        return None
