"""Dataclasses for Column, Filter, and Order configuration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class Column:
    """
    Specification for a list_display column.

    Supports both Django admin style (strings/callables) and
    enhanced configuration with additional metadata.

    New in Milestone 2:
        - filter: Filter configuration (for filtering plugins like djadmin-filters)
        - order: Ordering configuration (for ordering plugins like djadmin-filters)

    Attributes:
        field: Field name (string) or callable to display
        label: Optional override for column label
        empty_value: Display value for None/empty (default: '-')
        classes: CSS classes for this column
        filter: Filter configuration (True/False/Filter instance/None)
        order: Order configuration (True/False/Order instance/None)
    """

    field: str | Callable
    label: str | None = None  # Override auto-detected label
    empty_value: str = '-'  # Display for None/empty values
    classes: str = ''  # CSS classes for this column

    # Milestone 2: Optional filter/order support (requires appropriate plugins)
    filter: bool | Filter | None = None  # Filter config: True → Filter(), False/None → no filter
    order: bool | Order | None = None  # Order config: True → Order(), False/None → Order(enabled=False)

    @classmethod
    def from_field(cls, field):
        """
        Create Column from string or callable (Django admin compat).

        Args:
            field: String field name, callable, or Column instance

        Returns:
            Column instance
        """
        if isinstance(field, cls):
            return field
        return cls(field=field)

    @property
    def field_name(self):
        """Get field name as string (for template use)"""
        if callable(self.field):
            return getattr(self.field, '__name__', str(self.field))
        return str(self.field)

    @property
    def field_label(self):
        """Get label, falling back to field_name if not set"""
        return self.label if self.label is not None else self.field_name


@dataclass
class Filter:
    """
    Filter configuration for a Column.

    This dataclass wraps django-filter configuration and provides a clean API
    for specifying how a column should be filterable.

    Examples:
        # Simple exact match filter
        Column('category', filter=Filter())

        # Contains filter (case-insensitive)
        Column('name', filter=Filter(lookup_expr='icontains'))

        # Range filter (for numeric/date fields)
        Column('price', filter=Filter(lookup_expr=['gte', 'lte']))

        # Custom filter method
        Column('status', filter=Filter(method='filter_by_status'))

    Attributes:
        lookup_expr: The lookup expression(s) to use. Can be a string like 'exact',
                    'icontains', 'gte', or a list like ['gte', 'lte'] for ranges.
        widget: Optional Django form widget to use for the filter input.
        label: Optional custom label for the filter field.
        method: Optional method name or callable to use for custom filtering logic.
        exclude: If True, creates an exclude filter instead of a regular filter.
        distinct: If True, adds .distinct() to the queryset.
        field_class: Optional custom field class to use.
        extra: Additional kwargs to pass to django-filter.
    """

    lookup_expr: str | list[str] = 'exact'
    widget: type | None = None
    label: str | None = None
    method: str | Callable | None = None
    exclude: bool = False
    distinct: bool = False
    field_class: type | None = None
    extra: dict = field(default_factory=dict)

    def to_kwargs(self) -> dict:
        """
        Convert to django-filter kwargs.

        Returns:
            dict: Keyword arguments suitable for django-filter field creation.
        """
        kwargs = {
            'lookup_expr': self.lookup_expr,
            'exclude': self.exclude,
            'distinct': self.distinct,
        }

        if self.widget:
            kwargs['widget'] = self.widget
        if self.label:
            kwargs['label'] = self.label
        if self.method:
            kwargs['method'] = self.method
        if self.field_class:
            kwargs['field_class'] = self.field_class

        kwargs.update(self.extra)
        return kwargs


@dataclass
class Order:
    """
    Ordering configuration for a Column.

    This dataclass specifies how a column should be orderable, including
    custom labels and which fields to use for ordering.

    The Order instance is truthy when enabled=True and falsy when enabled=False,
    allowing for simple boolean checks: `if column.order: ...`

    Examples:
        # Enable ordering (default behavior)
        Column('name', order=Order())

        # Disable ordering
        Column('description', order=Order(enabled=False))

        # Custom labels for ascending/descending
        Column('price', order=Order(
            label='Price (low to high)',
            descending_label='Price (high to low)'
        ))

        # Order by multiple fields
        Column('author', order=Order(fields=['author__last_name', 'author__first_name']))

    Attributes:
        enabled: Whether ordering is enabled for this column.
        fields: Optional list of field names to use for ordering. If None, uses the column's field.
        label: Optional custom label for ascending order.
        descending_label: Optional custom label for descending order.
    """

    enabled: bool = True
    fields: list[str] | None = None
    label: str | None = None
    descending_label: str | None = None

    def __bool__(self):
        """Make Order truthy when enabled, falsy when disabled."""
        return self.enabled

    def to_ordering_choice(self, field_name: str, column_label: str):
        """
        Convert to OrderingFilter choice tuple.

        Args:
            field_name: The field name from the Column.
            column_label: The display label for the column.

        Returns:
            tuple: A tuple of (ascending_choice, descending_choice) for OrderingFilter,
                   or None if ordering is disabled.

        Example:
            >>> order = Order(label='Name (A-Z)', descending_label='Name (Z-A)')
            >>> order.to_ordering_choice('name', 'Name')
            (('name', 'Name (A-Z)'), ('-name', 'Name (Z-A)'))
        """
        if not self.enabled:
            return None

        # Use custom fields if specified, otherwise use the column's field
        base_field = self.fields[0] if self.fields else field_name
        asc_label = self.label or column_label
        desc_label = self.descending_label or f'{column_label} (desc)'

        return (
            (base_field, asc_label),
            (f'-{base_field}', desc_label),
        )


@dataclass
class SidebarWidget:
    """
    Sidebar widget for displaying content in action view sidebars.

    Sidebar widgets allow plugins to register content that appears in a dedicated
    sidebar area of action views (e.g., filters, quick actions, help text).

    Examples:
        # Simple widget with static template
        SidebarWidget(
            template='myapp/sidebar_widget.html',
            order=10,
        )

        # Widget with dynamic context
        SidebarWidget(
            template='djadmin_filters/filter_sidebar.html',
            context_callback=lambda action, request: {
                'filterset': action.get_filterset(),
            },
            order=10,
        )

        # Conditional widget (only show for certain views)
        SidebarWidget(
            template='myapp/help.html',
            condition=lambda action, request: action.model_admin.show_help,
            order=20,
        )

    Attributes:
        template: Path to the template to render for this widget.
        context_callback: Optional callable that receives (action, request) and returns
                         a dict of context variables for the template.
        order: Sort order for widgets (lower numbers appear first). Default: 10.
        condition: Optional callable that receives (action, request) and returns
                  True if the widget should be shown. Default: always show.
        identifier: Optional unique identifier for this widget (for debugging/overriding).
    """

    template: str
    context_callback: Callable[[Any, Any], dict] | None = None
    order: int = 10
    condition: Callable[[Any, Any], bool] | None = None
    identifier: str | None = None

    def should_display(self, view, request) -> bool:
        """
        Check if this widget should be displayed.

        Args:
            view: The view instance
            request: The HTTP request

        Returns:
            bool: True if the widget should be displayed
        """
        if self.condition is None:
            return True
        return self.condition(view, request)

    def get_context(self, view, request) -> dict:
        """
        Get context data for rendering this widget.

        Args:
            view: The view instance
            request: The HTTP request

        Returns:
            dict: Context variables for the template
        """
        if self.context_callback is None:
            return {}
        return self.context_callback(view, request)


@dataclass
class ColumnHeaderIcon:
    """
    Icon/button configuration for column headers in list views.

    Column header icons allow plugins to add interactive elements to table column
    headers (e.g., sort indicators, help text, filters). This provides a flexible
    extension point for any plugin to enhance column headers without template changes.

    Examples:
        # Sort indicator with URL
        ColumnHeaderIcon(
            icon_template='djadmin/icons/sort-up.html',
            url='?ordering=name',
            title='Sort by name (ascending)',
            order=10,
        )

        # Dynamic icon based on state
        ColumnHeaderIcon(
            icon_template=lambda col, view, req: (
                'djadmin/icons/sort-up.html' if req.GET.get('ordering') == col.field_name
                else 'djadmin/icons/sort.html'
            ),
            url=lambda col, view, req: f'?ordering={col.field_name}',
            title='Sort by this column',
            order=10,
        )

        # Help text icon
        ColumnHeaderIcon(
            icon_template='djadmin/icons/question.html',
            title='Click for help',
            css_class='help-icon',
            order=20,
        )

        # Conditional icon (only for certain columns)
        ColumnHeaderIcon(
            icon_template='djadmin/icons/filter.html',
            url='#filter-sidebar',
            condition=lambda column, view, request: column.filter is not None,
            order=5,
        )

    Attributes:
        icon_template: Path to SVG icon template to render, or callable that returns path.
        url: Optional URL to link to (if None, renders as span instead of link). Can be callable.
        title: Tooltip text for the icon. Can be callable.
        css_class: Additional CSS classes for the icon wrapper.
        order: Sort order for icons (lower numbers appear first). Default: 10.
        condition: Optional callable that receives (column, view, request) and returns
                  True if the icon should be shown. Default: always show.
        identifier: Optional unique identifier for this icon (for debugging/overriding).
    """

    icon_template: str | Callable[[Column, Any], str]
    url: str | Callable[[Column, Any], str] | None = None
    title: str | Callable[[Column, Any], str] = ''
    css_class: str = ''
    order: int = 10
    condition: Callable[[Column, Any], bool] | None = None
    identifier: str | None = None

    def should_display(self, column: Column, request) -> bool:
        """
        Check if this icon should be displayed for the given column.

        Args:
            column: The Column instance
            request: The HTTP request

        Returns:
            bool: True if the icon should be displayed
        """
        if self.condition is None:
            return True
        return self.condition(column, request)

    def get_icon_template(self, column: Column, request) -> str:
        """
        Get the icon template path (resolves callable if needed).

        Args:
            column: The Column instance
            request: The HTTP request

        Returns:
            str: Path to the icon template
        """
        if callable(self.icon_template):
            return self.icon_template(column, request)
        return self.icon_template

    def get_url(self, column: Column, request) -> str | None:
        """
        Get the URL for this icon (resolves callable if needed).

        Args:
            column: The Column instance
            request: The HTTP request

        Returns:
            str | None: The URL to link to, or None
        """
        if callable(self.url):
            return self.url(column, request)
        return self.url

    def get_title(self, column: Column, request) -> str:
        """
        Get the title text (resolves callable if needed).

        Args:
            column: The Column instance
            request: The HTTP request

        Returns:
            str: The title/tooltip text
        """
        if callable(self.title):
            return self.title(column, request)
        return self.title


@dataclass
class JSAsset:
    """
    JavaScript asset configuration for plugin-provided scripts.

    This dataclass specifies how JavaScript assets should be loaded, supporting
    modern module scripts, deferred loading, and async loading.

    Examples:
        # Render-blocking script (for web components to prevent layout shift)
        JSAsset(src='formset/js/django-formset.js', module=True, blocking=True)

        # Traditional script with defer
        JSAsset(src='djadmin/theme/js/admin.js', defer=True)

        # Async loading
        JSAsset(src='analytics/tracking.js', async_=True)

        # Fallback for browsers without module support
        JSAsset(src='legacy/polyfills.js', nomodule=True)

        # With Subresource Integrity
        JSAsset(
            src='https://cdn.example.com/library.js',
            integrity='sha384-...',
            crossorigin='anonymous'
        )

    Attributes:
        src: Static file path (relative to STATIC_URL).
        module: If True, adds type="module" attribute for ES modules.
        defer: If True, adds defer attribute (script executes after document is parsed).
        async_: If True, adds async attribute (script executes asynchronously).
        nomodule: If True, adds nomodule attribute (script only for non-module browsers).
        blocking: If True, script loads in <head> before rendering (prevents layout shift).
                  Use for critical scripts like web components. Default: False.
        integrity: Optional SRI hash for security.
        crossorigin: Optional CORS attribute ('anonymous' or 'use-credentials').
    """

    src: str
    module: bool = False
    defer: bool = False
    async_: bool = False  # Use async_ since 'async' is a Python keyword
    nomodule: bool = False
    blocking: bool = False  # If True, load in <head> before rendering (template placement directive)
    integrity: str | None = None
    crossorigin: str | None = None

    def get_attributes(self) -> dict[str, str | bool]:
        """
        Get HTML attributes for the script tag.

        Returns:
            dict: Mapping of attribute names to values.
                  Boolean True means attribute without value.
        """
        attrs = {}

        if self.module:
            attrs['type'] = 'module'
        if self.defer:
            attrs['defer'] = True
        if self.async_:
            attrs['async'] = True
        if self.nomodule:
            attrs['nomodule'] = True
        if self.integrity:
            attrs['integrity'] = self.integrity
        if self.crossorigin:
            attrs['crossorigin'] = self.crossorigin

        return attrs


@dataclass
class CSSAsset:
    """
    CSS asset configuration for plugin-provided stylesheets.

    This dataclass specifies how CSS assets should be loaded, supporting
    media queries and Subresource Integrity.

    Examples:
        # Standard stylesheet
        CSSAsset(href='djadmin/theme/css/theme.css')

        # Print-only stylesheet
        CSSAsset(href='djadmin/theme/css/print.css', media='print')

        # Responsive stylesheet
        CSSAsset(href='mobile.css', media='(max-width: 768px)')

        # With Subresource Integrity
        CSSAsset(
            href='https://cdn.example.com/styles.css',
            integrity='sha384-...',
            crossorigin='anonymous'
        )

    Attributes:
        href: Static file path (relative to STATIC_URL).
        media: Optional media query (e.g., 'print', '(max-width: 768px)').
        integrity: Optional SRI hash for security.
        crossorigin: Optional CORS attribute ('anonymous' or 'use-credentials').
    """

    href: str
    media: str | None = None
    integrity: str | None = None
    crossorigin: str | None = None

    def get_attributes(self) -> dict[str, str]:
        """
        Get HTML attributes for the link tag.

        Returns:
            dict: Mapping of attribute names to values.
        """
        attrs = {}

        if self.media:
            attrs['media'] = self.media
        if self.integrity:
            attrs['integrity'] = self.integrity
        if self.crossorigin:
            attrs['crossorigin'] = self.crossorigin

        return attrs
