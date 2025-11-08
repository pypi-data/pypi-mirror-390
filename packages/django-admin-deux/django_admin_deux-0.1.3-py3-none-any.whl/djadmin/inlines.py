"""Django admin compatibility layer for inline model admins.

These classes provide compatibility with Django's admin inline system,
but are deprecated in favor of the Layout API's Collection components.
"""

import warnings
from typing import ClassVar


class InlineModelAdmin:
    """
    Base class for inline model admins (Django admin compatibility).

    .. deprecated:: 1.0
        Use Collection components in ModelAdmin.layout instead.
        See: https://docs.django-admin-deux.dev/layout-api/collections/

    Attributes:
        model: The model class this inline represents
        fields: List of field names to display (default: all fields)
        extra: Number of extra empty forms to display (default: 1)
        min_num: Minimum number of forms required (default: 0)
        max_num: Maximum number of forms allowed (default: 1000)
        can_delete: Allow deletion of inline objects (default: True)
        verbose_name: Singular name for inline (default: model verbose_name)
        verbose_name_plural: Plural name for inline (default: model verbose_name_plural)
    """

    model = None
    fields = None
    extra = 1
    min_num = 0
    max_num = 1000
    can_delete = True
    verbose_name = None
    verbose_name_plural = None

    # Internal: display style for Collection conversion
    _display_style: ClassVar[str] = 'tabular'

    def __init_subclass__(cls, **kwargs):
        """Emit deprecation warning when inline class is created."""
        super().__init_subclass__(**kwargs)

        # Only warn for user-defined subclasses, not our own TabularInline/StackedInline
        if cls.__module__ != __name__:
            warnings.warn(
                f'{cls.__name__} inherits from InlineModelAdmin which is deprecated. '
                f'Use Collection components in ModelAdmin.layout instead. '
                f'See: https://docs.django-admin-deux.dev/layout-api/collections/',
                DeprecationWarning,
                stacklevel=2,
            )


class TabularInline(InlineModelAdmin):
    """
    Tabular inline admin (Django admin compatibility).

    Converts to Collection with display_style='tabular' (compact table layout).

    .. deprecated:: 1.0
        Use Collection components in ModelAdmin.layout instead.

    Example (deprecated):
        class OrderItemInline(TabularInline):
            model = OrderItem
            fields = ['product', 'quantity', 'price']
            extra = 1

        class OrderAdmin(ModelAdmin):
            inlines = [OrderItemInline]

    Recommended approach:
        from djadmin import ModelAdmin, Layout, Collection

        class OrderAdmin(ModelAdmin):
            layout = Layout(
                Field('customer'),
                Field('status'),
                Collection('orderitem_set',
                    model=OrderItem,
                    fields=['product', 'quantity', 'price'],
                    extra_siblings=1,
                    display_style='tabular',  # Compact table layout
                ),
            )
    """

    _display_style: ClassVar[str] = 'tabular'


class StackedInline(InlineModelAdmin):
    """
    Stacked inline admin (Django admin compatibility).

    Converts to Collection with display_style='stacked' (vertical form layout).

    .. deprecated:: 1.0
        Use Collection components in ModelAdmin.layout instead.

    Example (deprecated):
        class OrderItemInline(StackedInline):
            model = OrderItem
            fields = ['product', 'quantity', 'price']
            extra = 1

        class OrderAdmin(ModelAdmin):
            inlines = [OrderItemInline]

    Recommended approach:
        from djadmin import ModelAdmin, Layout, Collection

        class OrderAdmin(ModelAdmin):
            layout = Layout(
                Field('customer'),
                Field('status'),
                Collection('orderitem_set',
                    model=OrderItem,
                    fields=['product', 'quantity', 'price'],
                    extra_siblings=1,
                    display_style='stacked',  # Vertical form layout
                ),
            )
    """

    _display_style: ClassVar[str] = 'stacked'
