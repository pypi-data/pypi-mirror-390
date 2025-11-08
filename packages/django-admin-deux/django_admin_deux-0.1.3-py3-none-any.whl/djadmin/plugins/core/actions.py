"""Default CRUD actions provided by core plugin"""

from djadmin.actions import BaseAction, BulkActionMixin, FormFeaturesMixin, GeneralActionMixin, RecordActionMixin
from djadmin.actions.base import WithSuccessUrlActionMixin
from djadmin.actions.view_mixins import (
    BulkDeleteViewActionMixin,
    CreateViewActionMixin,
    DeleteViewActionMixin,
    DetailViewActionMixin,
    ListViewActionMixin,
    UpdateViewActionMixin,
)


class ModelFormActionMixin(WithSuccessUrlActionMixin, FormFeaturesMixin):
    _action_map = {
        'add': 'create',
        'edit': 'update',
    }

    def get_layout(self):
        name = self.action._action_map.get(self.action.action_name, self.action.action_name)
        return getattr(self, f'{name}_layout', None) or self.layout

    def get_form_class(self):
        """Get form class - returns explicit form_class or delegates to build_form()."""
        # Validate that required features are available
        self.validate_features()

        print('get_form_class called')

        # Check for explicit form_class (action-specific or general)
        name = self.action._action_map.get(self.action.action_name, self.action.action_name)
        if form_class := getattr(self, f'{name}_form_class', None) or self.form_class:
            return form_class

        # No explicit form - delegate to build_form() (defined on view)
        return self.build_form()


class AddAction(ModelFormActionMixin, GeneralActionMixin, CreateViewActionMixin, BaseAction):
    """
    Action to add a new record.

    Displays a form to create a new instance of the model.
    Uses CreateViewActionMixin to generate a CreateView via ViewFactory.
    """

    label = 'Add'
    icon = 'plus'
    css_class = 'primary'
    django_permission_name = 'add'  # Django permission for creating records

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for Add action.

        Uses __new__ convention instead of /actions/ prefix.

        Returns:
            URL pattern string (e.g., 'webshop/category/__new__/')
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/__new__/'


class EditAction(ModelFormActionMixin, RecordActionMixin, UpdateViewActionMixin, BaseAction):
    """
    Action to edit an existing record.

    Displays a form to update the selected instance.
    Uses UpdateViewActionMixin to generate an UpdateView via ViewFactory.
    """

    label = 'Edit'
    icon = 'pencil'
    css_class = 'primary'
    django_permission_name = 'change'  # Django permission for updating records
    _url_name = 'edit'


class DeleteAction(WithSuccessUrlActionMixin, RecordActionMixin, DeleteViewActionMixin, BaseAction):
    """
    Action to delete a single record.

    Shows confirmation page before deleting.
    Uses DeleteViewActionMixin to generate a DeleteView via ViewFactory.
    """

    label = 'Delete'
    icon = 'trash'
    css_class = 'danger'
    django_permission_name = 'delete'  # Django permission for deleting records
    confirmation_required = True
    _url_name = 'delete'

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for Delete action.

        Returns:
            URL pattern string with pk parameter
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/<int:pk>/delete/'


class DeleteBulkAction(WithSuccessUrlActionMixin, BulkActionMixin, BulkDeleteViewActionMixin, BaseAction):
    """
    Action to delete multiple selected records.

    Shows confirmation page with count before deleting.
    Uses BulkDeleteViewActionMixin to generate a BulkDeleteView via ViewFactory.
    """

    label = 'Delete Selected'
    icon = 'trash'
    django_permission_name = 'delete'  # Django permission for deleting records
    confirmation_required = True
    _url_name = 'bulk_delete'

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for Bulk Delete action.

        Returns:
            URL pattern string
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/bulk_delete/'


class ViewAction(RecordActionMixin, DetailViewActionMixin, BaseAction):
    """
    Action to view a record in read-only mode.

    Shows record details using the Layout API for structured display.
    Only visible when user has 'view' permission but NOT 'change' permission.
    """

    label = 'View'
    icon = 'eye'
    css_class = 'secondary'
    django_permission_name = 'view'  # Django permission for viewing records
    _url_name = 'view'

    def __init__(self, *args, **kwargs):
        """Initialize with permission that only shows for view-only users."""
        # Set permission: IsStaff & view permission & NOT change permission
        # This ensures the action only shows for users who can view but not edit
        from djadmin.plugins.permissions import HasDjangoPermission, IsStaff

        kwargs.setdefault(
            'permission_class', IsStaff() & HasDjangoPermission(perm='view') & ~HasDjangoPermission(perm='change')
        )
        super().__init__(*args, **kwargs)

    def get_url_pattern(self) -> str:
        """
        Get URL pattern for View action.

        Returns:
            URL pattern string with pk parameter
        """
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/<int:pk>/view/'


class ListAction(ListViewActionMixin, BaseAction):
    """
    Built-in action for generating ListView.

    This action is automatically created by AdminSite for each registered
    model to provide the main list view. It's not meant to be instantiated
    directly by users.

    The action combines ListViewActionMixin (which specifies ListView as
    base_class) with BaseAction to create a complete action that can be
    passed to ViewFactory.

    Example usage (internal to AdminSite):
        list_action = ListViewAction(model, model_admin, admin_site)
        factory = ViewFactory()
        list_view_class = factory.create_view(list_action)
    """

    label = 'List'
    css_class = 'secondary'  # Use secondary/outline style for list links
    django_permission_name = 'view'  # Django permission for viewing list

    def get_url_pattern(self):
        opts = self.model._meta
        return f'{opts.app_label}/{opts.model_name}/'

    def get_queryset(self):
        """
        Get queryset for list view with ordering and plugin modifications.

        When this method is copied to the view class, 'self' will be the view instance.
        The view has model_admin, request, etc. as attributes.

        Returns:
            QuerySet for the model
        """
        from djadmin.plugins import pm

        # Call super to get base queryset from ListView
        # Use type(self).__mro__[1] to get the parent class in the view's MRO
        # This works because when copied to the view, self is the view instance
        queryset = super(type(self), self).get_queryset()

        # Apply ordering from model_admin (view has this as an attribute)
        if hasattr(self, 'ordering') and self.ordering:
            queryset = queryset.order_by(*self.ordering)

        # Allow plugins to modify queryset
        plugin_results = pm.hook.djadmin_modify_queryset(
            queryset=queryset,
            request=self.request,
            view=self,
        )

        # Use the last non-None result
        for result in reversed(plugin_results):
            if result is not None:
                queryset = result
                break

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add list_display to template context.

        When bound to the view, self is the view instance.
        Calls DjAdminViewMixin.get_context_data() via super() to get base admin context.

        Note: Action filtering is now handled automatically by DjAdminViewMixin.get_context_data()
        """
        # Call super to get base context from DjAdminViewMixin
        # This now includes filtered actions automatically
        context = super(type(self), self).get_context_data(**kwargs)

        # Add list_display for template iteration
        context['list_display'] = self.model_admin.list_display

        return context
