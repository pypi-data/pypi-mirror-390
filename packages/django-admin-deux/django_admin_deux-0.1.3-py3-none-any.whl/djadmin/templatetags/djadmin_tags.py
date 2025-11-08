"""Template tags for django-admin-deux"""

from django import template
from django.core.exceptions import FieldDoesNotExist

register = template.Library()


@register.simple_tag
def get_column_value(obj, column, model_admin):
    """
    Get the value for a list_display column.

    Supports:
    - Model field names: 'name', 'category__name'
    - Model properties: 'is_in_stock'
    - Model methods: 'get_absolute_url'
    - Callables: lambda obj: obj.price * 1.2
    - ModelAdmin methods: 'formatted_price'
    - Column objects: Column('name', empty_value='N/A')

    Args:
        obj: Model instance
        column: Column object (normalized by metaclass)
        model_admin: ModelAdmin instance

    Returns:
        The value to display
    """
    from djadmin.options import Column

    # Extract field and empty_value from Column object
    if isinstance(column, Column):
        field = column.field
        empty_value = column.empty_value
    else:
        field = column
        empty_value = '-'

    # If it's a callable, call it with obj
    if callable(field):
        value = field(obj)
    # Try to get attribute from object FIRST (before checking ModelAdmin)
    elif hasattr(obj, field):
        value = getattr(obj, field, None)
        # If it's callable (method or property), call it
        if callable(value):
            try:
                value = value()
            except TypeError:
                # Property without ()
                pass
    # Handle related lookups (e.g., 'category__name')
    elif isinstance(field, str) and '__' in field:
        parts = field.split('__')
        value = obj
        for part in parts:
            if value is None:
                break
            value = getattr(value, part, None)
    # Check if it's a ModelAdmin method (fallback)
    elif hasattr(model_admin, field):
        attr = getattr(model_admin, field)
        if callable(attr):
            value = attr(obj)
        else:
            value = attr
    # No attribute found
    else:
        value = None

    # Handle None/empty values
    if value is None or value == '':
        return empty_value

    return value


@register.simple_tag
def get_column_label(column, model, model_admin):
    """
    Get the label for a list_display column.

    Args:
        column: Column object (normalized by metaclass)
        model: The model class
        model_admin: ModelAdmin instance

    Returns:
        Column label string
    """
    from djadmin.options import Column

    # Extract field and label from Column object
    if isinstance(column, Column):
        if column.label:
            return column.label
        field = column.field
    else:
        field = column

    # Special case for __str__
    if field == '__str__':
        return str(model._meta.verbose_name).title()

    # If it's a callable, try to get its short_description
    if callable(field):
        if hasattr(field, 'short_description'):
            return field.short_description
        return getattr(field, '__name__', str(field))

    # Check for ModelAdmin method with short_description
    if hasattr(model_admin, field):
        attr = getattr(model_admin, field)
        if callable(attr) and hasattr(attr, 'short_description'):
            return attr.short_description

    # Handle related lookups
    if isinstance(field, str) and '__' in field:
        parts = field.split('__')
        current_model = model
        for part in parts[:-1]:
            try:
                field_obj = current_model._meta.get_field(part)
                current_model = field_obj.related_model
            except FieldDoesNotExist:
                break
        field = parts[-1]

    # Try to get field verbose name
    try:
        field_obj = model._meta.get_field(field)
        return field_obj.verbose_name.title()
    except FieldDoesNotExist:
        pass

    # Fallback: humanize the field name
    return str(field).replace('_', ' ').title()


@register.simple_tag
def get_column_classes(column):
    """
    Get CSS classes for a column.

    Args:
        column: Column object

    Returns:
        String of CSS classes
    """
    from djadmin.options import Column

    if isinstance(column, Column):
        return column.classes
    return ''


@register.inclusion_tag('djadmin/includes/_column_header_icons.html', takes_context=True)
def render_column_header_icons(context, column):
    """
    Render icons for a column header.

    Filters column_header_icons from context based on each icon's condition,
    then resolves any callable attributes (icon_template, url, title) for display.

    Args:
        context: Template context (contains request, column_header_icons)
        column: Column instance

    Returns:
        Dict with 'icons' list for template rendering
    """
    request = context.get('request')
    all_icons = context.get('column_header_icons', [])

    if not request or not all_icons:
        return {'icons': []}

    # Filter icons that should display for this column
    icons_to_render = []
    for icon in all_icons:
        if icon.should_display(column, request):
            # Resolve callable attributes
            icon_data = {
                'icon_template': icon.get_icon_template(column, request),
                'url': icon.get_url(column, request),
                'title': icon.get_title(column, request),
                'css_class': icon.css_class,
            }
            icons_to_render.append(icon_data)

    return {'icons': icons_to_render}


@register.simple_tag(takes_context=True)
def query_params_as_hidden_inputs(context, *exclude):
    """
    Convert current query parameters to hidden input fields.

    This allows forms to preserve query parameters from other features
    (e.g., search form preserves filters, filter form preserves search).

    Usage:
        <form method="get" action="">
            {% query_params_as_hidden_inputs 'search' 'page' %}
            <input type="search" name="search" value="...">
            <button type="submit">Search</button>
        </form>

        {# With filterset field names #}
        {% query_params_as_hidden_inputs 'page' filterset.form.fields %}

    Args:
        context: Template context (contains request)
        *exclude: Parameter names to exclude from hidden inputs.
                 Can be strings or dict_keys objects (from form.fields)

    Returns:
        Safe HTML string of hidden input elements
    """
    from django.utils.html import format_html
    from django.utils.safestring import mark_safe

    request = context.get('request')
    if not request:
        return mark_safe('')

    # Flatten exclude into a set of strings
    exclude_set = set()
    for item in exclude:
        if isinstance(item, str):
            exclude_set.add(item)
        else:
            # Handle dict_keys, lists, tuples, etc.
            try:
                exclude_set.update(item)
            except TypeError:
                # If it's not iterable, just add it as a string
                exclude_set.add(str(item))

    # Build list of hidden inputs
    hidden_inputs = []
    for key in request.GET:
        # Skip excluded parameters
        if key in exclude_set:
            continue

        # Handle multiple values for the same key
        values = request.GET.getlist(key)
        for value in values:
            hidden_inputs.append(format_html('<input type="hidden" name="{}" value="{}">', key, value))

    return mark_safe('\n'.join(hidden_inputs))


@register.simple_tag(takes_context=True)
def filter_record_actions(context, actions, obj):
    """
    Filter record actions for a specific object based on user permissions.

    This tag is used in ListView to filter actions per-row, since each row
    represents a different object and may have different permissions.

    Args:
        context: Template context (provides request)
        actions: List of action instances to filter
        obj: Specific object instance to check permissions for

    Returns:
        List of actions that the user has permission to execute on this object

    Example:
        {% filter_record_actions record_actions obj as filtered_actions %}
        {% for action in filtered_actions %}
            <a href="...">{{ action.label }}</a>
        {% endfor %}
    """
    request = context.get('request')
    model_admin = context.get('model_admin')

    if not request or not model_admin or not actions:
        return []

    return model_admin.filter_actions(actions, request, obj=obj)


@register.simple_tag
def assign(value):
    """
    Simple assignment tag that returns the value passed to it.

    Useful for conditionally assigning values in templates.

    Example:
        {% if object %}
            {% assign filtered_actions as actions %}
        {% else %}
            {% filter_record_actions actions object as actions %}
        {% endif %}
    """
    return value
