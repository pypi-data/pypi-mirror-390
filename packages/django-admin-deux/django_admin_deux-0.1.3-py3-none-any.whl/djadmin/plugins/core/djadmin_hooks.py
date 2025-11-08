from djadmin.plugins import hookimpl


@hookimpl
def djadmin_provides_features():
    return ['crud', 'search']


@hookimpl
def djadmin_get_default_general_actions():
    """Provide default general actions (main entry points)"""
    from djadmin.plugins.core.actions import ListAction

    from .actions import AddAction

    return [ListAction, AddAction]


@hookimpl
def djadmin_get_default_bulk_actions():
    """Provide default bulk actions"""
    from .actions import DeleteBulkAction

    return [DeleteBulkAction]


@hookimpl
def djadmin_get_default_record_actions():
    """Provide default record actions"""
    from .actions import DeleteAction, EditAction, ViewAction

    return [ViewAction, EditAction, DeleteAction]


@hookimpl
def djadmin_get_action_view_mixins(action):
    """
    Register view mixins for actions.

    Returns a registry mapping action classes to lists of mixin classes.
    DjAdminViewMixin is applied to all actions to provide base get_context_data.
    RedirectViewMixin is applied to RedirectViewActionMixin actions.
    SearchMixin is applied to ListViewAction when search_fields is configured.
    """
    from djadmin.actions.base import BaseAction
    from djadmin.actions.view_mixins import RedirectViewActionMixin
    from djadmin.plugins.core.actions import ListAction

    from .mixins import DjAdminViewMixin, RedirectViewMixin, SearchMixin

    return {
        BaseAction: [DjAdminViewMixin],  # All actions get the base mixin
        RedirectViewActionMixin: [RedirectViewMixin],  # Redirect actions get redirect dispatch
        ListAction: [SearchMixin],
    }


@hookimpl
def djadmin_get_action_view_attribute_bindings(action):
    """
    Register attribute bindings for actions.

    Returns a registry mapping action classes to lists of attribute names.
    These attributes will be bound from the action to the view.
    """
    from djadmin.actions.base import BaseAction, WithSuccessUrlActionMixin
    from djadmin.actions.dashboard import DashboardAction
    from djadmin.actions.view_mixins import (
        BulkDeleteViewActionMixin,
        DeleteViewActionMixin,
        DetailViewActionMixin,
        FormFeaturesMixin,
        FormViewActionMixin,
        ListViewActionMixin,
        TemplateViewActionMixin,
    )

    from .actions import ModelFormActionMixin

    return {
        BaseAction: ['get_template_names'],  # All actions provide templates
        ListViewActionMixin: ['get_queryset', 'get_context_data'],  # ListView actions provide queryset and context
        TemplateViewActionMixin: ['get_context_data'],  # TemplateView actions can override context
        FormFeaturesMixin: ['get_form_features', 'validate_features'],  # Feature detection and validation
        FormViewActionMixin: ['get_form_class', 'get_success_url'],  # Non-model form actions
        WithSuccessUrlActionMixin: ['get_success_url'],  # Create, Update or Delete actions
        ModelFormActionMixin: ['get_layout', 'get_form_class', 'get_fields'],  # Create or Update actions
        DetailViewActionMixin: ['get_layout', 'get_context_data'],  # Detail view actions
        DeleteViewActionMixin: ['get_success_url'],  # Delete actions
        BulkDeleteViewActionMixin: ['get_success_url', 'get_queryset'],  # Bulk delete actions
        DashboardAction: [
            'get_template_names',
            '_get_app_context',
            '_get_all_apps_context',
            '_get_model_admins_for_app',
            '_get_action_data',
        ],  # Dashboard-specific helper methods
    }


@hookimpl
def djadmin_get_action_view_attributes(action):
    """
    Provide view attributes for actions.

    Returns a registry mapping action classes to attribute dicts.
    """
    from djadmin.actions.view_mixins import CreateViewActionMixin, ListViewActionMixin, UpdateViewActionMixin

    from .utils import copy_model_admin_attrs

    return {
        ListViewActionMixin: copy_model_admin_attrs(action, ['paginate_by']),
        UpdateViewActionMixin: copy_model_admin_attrs(
            action, ['layout', 'update_layout', 'form_class', 'update_form_class']
        ),
        CreateViewActionMixin: copy_model_admin_attrs(
            action, ['layout', 'create_layout', 'form_class', 'create_form_class']
        ),
    }


@hookimpl
def djadmin_add_context_data(context, request, view):
    """
    Add pagination helpers to context for ListView.

    Django's ListView automatically adds:
    - paginator: Paginator instance
    - page_obj: Page instance (if paginated)
    - is_paginated: Boolean
    - object_list: Current page's objects

    We add:
    - page_range: Smart page range for pagination display
    - show_first: Boolean to show "first page" link
    - show_last: Boolean to show "last page" link
    """
    # Only add pagination helpers if this is a paginated view
    if not context.get('is_paginated'):
        return {}

    page_obj = context.get('page_obj')
    if not page_obj:
        return {}

    # Calculate smart page range
    page_range = _get_page_range(page_obj)

    return {
        'page_range': page_range,
        'show_first': page_obj.number > 3,
        'show_last': page_obj.number < page_obj.paginator.num_pages - 2,
    }


def _get_page_range(page_obj):
    """
    Get smart page range for pagination display.

    Shows pages around current page, e.g.:
    [1] ... [5] [6] [7] [8] [9] ... [50]

    Returns:
        List of page numbers (and None for ellipsis)
    """
    paginator = page_obj.paginator
    current = page_obj.number
    num_pages = paginator.num_pages

    # Always show first and last
    # Show 2 pages on each side of current
    page_range = []

    # First page
    page_range.append(1)

    # Pages around current
    start = max(2, current - 2)
    end = min(num_pages - 1, current + 2)

    if start > 2:
        page_range.append(None)  # Ellipsis

    page_range.extend(range(start, end + 1))

    if end < num_pages - 1:
        page_range.append(None)  # Ellipsis

    # Last page
    if num_pages > 1:
        page_range.append(num_pages)

    return page_range


@hookimpl
def djadmin_get_sidebar_widgets(action):
    """
    Provide search widget for ListView when search_fields is configured.

    Returns a registry mapping action classes to lists of SidebarWidget instances.
    """
    from djadmin.dataclasses import SidebarWidget
    from djadmin.plugins.core.actions import ListAction

    # Only provide search widget for ListViewAction with search_fields
    if not isinstance(action, ListAction):
        return {}

    search_fields = getattr(action.model_admin, 'search_fields', None)
    if not search_fields:
        return {}

    # Create search widget with order=0 to display at top of sidebar
    search_widget = SidebarWidget(
        template='djadmin/includes/search_widget.html',
        order=0,  # Display before other widgets (filters have order=10)
        identifier='search',
    )

    return {ListAction: [search_widget]}


@hookimpl
def djadmin_get_test_methods():
    """
    Provide default test methods for core CRUD actions.

    Returns mapping of action base classes to test method callables.
    These are the standard tests for Django forms (not FormCollection).
    """
    from djadmin.actions.view_mixins import (
        CreateViewActionMixin,
        DeleteViewActionMixin,
        ListViewActionMixin,
        UpdateViewActionMixin,
    )

    #  Define test method implementations

    def test_list(test_case, action):
        """Test GET request to list view."""
        url = test_case._get_action_url(action)
        response = test_case.client.get(url)

        test_case.assertEqual(response.status_code, 200, f'List GET failed for {action.__class__.__name__}')
        test_case.assertIn(
            test_case.obj, response.context['object_list'], f'Object not in list for {action.__class__.__name__}'
        )

    def test_create_get(test_case, action):
        """Test GET request to create view."""
        url = test_case._get_action_url(action)
        response = test_case.client.get(url)

        test_case.assertEqual(response.status_code, 200, f'Create GET failed for {action.__class__.__name__}')
        test_case.assertIn('form', response.context, f'No form in context for {action.__class__.__name__}')

    def test_create_post(test_case, action):
        """Test POST request to create view."""
        url = test_case._get_action_url(action)
        data = test_case.get_create_data()

        # Count before create
        count_before = test_case.model.objects.count()

        response = test_case.client.post(url, data)

        # Should redirect or show success (200 if form re-rendered with success)
        test_case.assertIn(
            response.status_code,
            [200, 302],
            f'Create POST failed for {action.__class__.__name__}: {response.status_code}',
        )

        # Object should be created
        test_case.assertEqual(
            test_case.model.objects.count(),
            count_before + 1,
            f'Object not created for {action.__class__.__name__}',
        )

        # Custom assertions
        test_case.assert_create_successful(response, data)

    def test_update_get(test_case, action):
        """Test GET request to update view."""
        url = test_case._get_action_url(action, test_case.obj)
        response = test_case.client.get(url)

        test_case.assertEqual(response.status_code, 200, f'Update GET failed for {action.__class__.__name__}')
        test_case.assertIn('form', response.context, f'No form in context for {action.__class__.__name__}')

        # Form should be pre-filled with current data
        form = response.context['form']
        test_case.assertEqual(
            form.instance.pk, test_case.obj.pk, f'Form not pre-filled for {action.__class__.__name__}'
        )

    def test_update_post(test_case, action):
        """Test POST request to update view."""
        url = test_case._get_action_url(action, test_case.obj)
        data = test_case.get_update_data(test_case.obj)

        response = test_case.client.post(url, data)

        # Should redirect or show success
        test_case.assertIn(
            response.status_code,
            [200, 302],
            f'Update POST failed for {action.__class__.__name__}: {response.status_code}',
        )

        # Object should be updated
        test_case.obj.refresh_from_db()
        for field, value in test_case.to_update_fields.items():
            test_case.assertEqual(
                getattr(test_case.obj, field),
                value,
                f'Field {field} not updated for {action.__class__.__name__}',
            )

        # Custom assertions
        test_case.assert_update_successful(response, test_case.obj, data)

    def test_delete(test_case, action):
        """Test POST request to delete view."""
        # Create new object to delete (don't delete test_case.obj, other tests need it)
        kwargs = test_case.get_factory_delete_kwargs()
        obj_to_delete = test_case.model_factory_class.create(**kwargs)

        url = test_case._get_action_url(action, obj_to_delete)

        # Count before delete
        count_before = test_case.model.objects.count()

        response = test_case.client.post(url, {'confirm': 'yes'})

        # Should redirect to list
        test_case.assertEqual(response.status_code, 302, f'Delete failed for {action.__class__.__name__}')

        # Object should be deleted
        test_case.assertEqual(
            test_case.model.objects.count(),
            count_before - 1,
            f'Object not deleted for {action.__class__.__name__}',
        )
        test_case.assertFalse(
            test_case.model.objects.filter(pk=obj_to_delete.pk).exists(),
            f'Object still exists after delete for {action.__class__.__name__}',
        )

        # Custom assertions
        test_case.assert_delete_successful(response, obj_to_delete)

    # Return mapping
    return {
        ListViewActionMixin: {
            '_test_list': test_list,
        },
        CreateViewActionMixin: {
            '_test_create_get': test_create_get,
            '_test_create_post': test_create_post,
        },
        UpdateViewActionMixin: {
            '_test_update_get': test_update_get,
            '_test_update_post': test_update_post,
        },
        DeleteViewActionMixin: {
            '_test_delete': test_delete,
        },
    }


@hookimpl
def djadmin_get_required_apps():
    """Core plugin apps."""
    return [
        'djadmin.plugins.core',
        # Core has no Before/After requirements
    ]
