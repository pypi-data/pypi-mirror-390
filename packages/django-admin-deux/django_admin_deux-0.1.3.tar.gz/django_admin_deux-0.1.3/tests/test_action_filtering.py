"""Tests for permission-aware action filtering in ListView and ModelAdmin.

Tests the check_permission() method on actions and the filter_actions()
method on ModelAdmin.
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from djadmin import ModelAdmin, site
from djadmin.actions.base import BaseAction, GeneralActionMixin
from djadmin.plugins.permissions import HasDjangoPermission, IsStaff, IsSuperuser
from examples.webshop.factories import ProductFactory
from examples.webshop.models import Product
from tests.conftest import RegistrySaveRestoreMixin
from tests.factories import UserFactory


# Test fixtures for different permission scenarios
class ViewOnlyProductAdmin(ModelAdmin):
    """Admin with view permission only."""

    permission_class = IsStaff() & HasDjangoPermission(perm='view')


class ChangeOnlyProductAdmin(ModelAdmin):
    """Admin with change permission only."""

    permission_class = IsStaff() & HasDjangoPermission(perm='change')


class SuperuserOnlyProductAdmin(ModelAdmin):
    """Admin accessible only to superusers."""

    permission_class = IsSuperuser()


class NoPermissionProductAdmin(ModelAdmin):
    """Admin with no permission checks."""

    permission_class = None


# Custom test action for permission testing
class CustomTestAction(GeneralActionMixin, BaseAction):
    """Custom action for testing permission filtering."""

    label = 'Custom Test Action'
    permission_class = IsStaff()

    def get_template_name(self):
        return 'djadmin/model_list.html'


class TestActionCheckPermission(RegistrySaveRestoreMixin, TestCase):
    """Test the check_permission() method on BaseAction."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.product = ProductFactory()

        # Create users with different permission levels
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.staff_with_view = UserFactory(is_staff=True)
        self.staff_no_perms = UserFactory(is_staff=True)
        self.regular_user = UserFactory(is_staff=False)

        # Grant view permission to staff_with_view
        content_type = ContentType.objects.get_for_model(Product)
        view_perm = Permission.objects.get(codename='view_product', content_type=content_type)
        self.staff_with_view.user_permissions.add(view_perm)

    def test_superuser_has_permission_for_all_actions(self):
        """Superusers should pass permission checks for all actions."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.superuser

        # Get an action from the model_admin
        action = model_admin.general_actions[0] if model_admin.general_actions else None
        assert action is not None, 'Expected general_actions to have at least one action'

        # Check permission
        result = action.check_permission(request)
        assert result is True, 'Superuser should have permission for all actions'

    def test_regular_user_denied_for_staff_only_actions(self):
        """Regular users (non-staff) should be denied for IsStaff actions."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.regular_user

        # Get an action
        action = model_admin.general_actions[0] if model_admin.general_actions else None
        assert action is not None

        # Check permission - should be denied
        result = action.check_permission(request)
        assert result is False, 'Regular user should be denied for IsStaff & HasDjangoPermission actions'

    def test_staff_with_permission_allowed(self):
        """Staff with correct Django permission should pass check."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.staff_with_view

        # Get an action
        action = model_admin.general_actions[0] if model_admin.general_actions else None
        assert action is not None

        # Check permission - should pass (staff + view permission)
        result = action.check_permission(request)
        assert result is True, 'Staff with view permission should pass for view-only actions'

    def test_staff_without_permission_denied(self):
        """Staff without correct Django permission should be denied."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.staff_no_perms

        # Get an action
        action = model_admin.general_actions[0] if model_admin.general_actions else None
        assert action is not None

        # Check permission - should be denied (staff but no view permission)
        result = action.check_permission(request)
        assert result is False, 'Staff without view permission should be denied'

    def test_no_permission_class_allows_all(self):
        """Actions with permission_class=None should allow all users."""
        site.register(Product, NoPermissionProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.regular_user  # Even non-staff user

        # Get an action
        action = model_admin.general_actions[0] if model_admin.general_actions else None
        assert action is not None

        # Check permission - should pass (no permission check)
        result = action.check_permission(request)
        assert result is True, 'Actions with permission_class=None should allow all users'

    def test_action_level_permission_override(self):
        """Action-level permission_class should override ModelAdmin default."""

        # Create a custom action with IsSuperuser permission
        class SuperuserOnlyAction(GeneralActionMixin, BaseAction):
            label = 'Superuser Only'
            permission_class = IsSuperuser()

            def get_template_name(self):
                return 'djadmin/model_list.html'

        # Register with ViewOnlyProductAdmin but add custom action
        class CustomAdmin(ViewOnlyProductAdmin):
            general_actions = [SuperuserOnlyAction]

        site.register(Product, CustomAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.staff_with_view  # Staff with view perm, but NOT superuser

        # Get the custom action
        action = model_admin.general_actions[0]
        assert action.label == 'Superuser Only'

        # Check permission - should be denied (requires superuser)
        result = action.check_permission(request)
        assert result is False, 'Staff with view perm should be denied for superuser-only action'

        # Try with superuser
        request.user = self.superuser
        result = action.check_permission(request)
        assert result is True, 'Superuser should pass for superuser-only action'


class TestModelAdminFilterActions(RegistrySaveRestoreMixin, TestCase):
    """Test the filter_actions() method on ModelAdmin."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.product = ProductFactory()

        # Create users
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.staff_with_view = UserFactory(is_staff=True)
        self.regular_user = UserFactory(is_staff=False)

        # Grant view permission to staff_with_view
        content_type = ContentType.objects.get_for_model(Product)
        view_perm = Permission.objects.get(codename='view_product', content_type=content_type)
        self.staff_with_view.user_permissions.add(view_perm)

    def test_filter_actions_with_superuser(self):
        """Superuser should see all actions."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.superuser

        # Filter actions
        all_actions = model_admin.general_actions
        filtered = model_admin.filter_actions(all_actions, request)

        # Superuser should see all actions
        assert len(filtered) == len(all_actions), 'Superuser should see all actions'

    def test_filter_actions_with_view_only_user(self):
        """User with view permission should see view-only actions."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.staff_with_view

        # Filter actions
        all_actions = model_admin.general_actions
        filtered = model_admin.filter_actions(all_actions, request)

        # Should see actions (has view permission)
        assert len(filtered) > 0, 'User with view permission should see actions'

    def test_filter_actions_with_regular_user(self):
        """Regular user (non-staff) should see no actions with IsStaff requirement."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.regular_user

        # Filter actions
        all_actions = model_admin.general_actions
        filtered = model_admin.filter_actions(all_actions, request)

        # Regular user should see no actions (IsStaff required)
        assert len(filtered) == 0, 'Regular user should see no actions with IsStaff requirement'

    def test_filter_actions_with_no_permission_admin(self):
        """Admin with permission_class=None should show all actions to all users."""
        site.register(Product, NoPermissionProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.regular_user  # Even regular user

        # Filter actions
        all_actions = model_admin.general_actions
        filtered = model_admin.filter_actions(all_actions, request)

        # Should see all actions (no permission check)
        assert len(filtered) == len(all_actions), 'All users should see actions when permission_class=None'

    def test_filter_empty_action_list(self):
        """filter_actions() should handle empty action list gracefully."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.superuser

        # Filter empty list
        filtered = model_admin.filter_actions([], request)

        # Should return empty list
        assert filtered == [], 'Empty action list should return empty list'


class TestListViewActionFiltering(RegistrySaveRestoreMixin, TestCase):
    """Test action filtering in ListView context."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.product = ProductFactory()

        # Create users
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.staff_with_view = UserFactory(is_staff=True)
        self.regular_user = UserFactory(is_staff=False)

        # Grant view permission to staff_with_view
        content_type = ContentType.objects.get_for_model(Product)
        view_perm = Permission.objects.get(codename='view_product', content_type=content_type)
        self.staff_with_view.user_permissions.add(view_perm)

    def test_superuser_sees_all_actions_in_list_view(self):
        """Superuser should see all actions in list view."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.superuser)

        # Get list view
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that filtered_general_actions are present
        assert 'filtered_general_actions' in response.context
        assert len(response.context['filtered_general_actions']) > 0

    def test_view_only_user_sees_filtered_actions(self):
        """User with view permission should see filtered actions."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.staff_with_view)

        # Get list view
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that actions are present (user has view permission)
        assert 'filtered_general_actions' in response.context
        assert len(response.context['filtered_general_actions']) > 0

    def test_regular_user_sees_no_actions(self):
        """Regular user should see no actions in staff-only admin."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.regular_user)

        # Try to access list view - should be denied at view level
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        # Should be redirected or 403
        assert response.status_code in [302, 403], 'Regular user should be denied access'

    def test_object_list_has_available_record_actions(self):
        """Record actions should be filtered in list view context."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.superuser)

        # Get list view
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that record_actions are in context and filtered
        assert 'record_actions' in response.context
        assert isinstance(response.context['record_actions'], list)
        # Superuser should have access to all record actions
        assert len(response.context['record_actions']) > 0

    def test_bulk_actions_filtered_in_context(self):
        """Bulk actions should be filtered in list view context."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.staff_with_view)

        # Get list view
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that bulk_actions are present and filtered
        assert 'bulk_actions' in response.context
        # Should be a list (even if empty)
        assert isinstance(response.context['bulk_actions'], list)

    def test_record_actions_filtered_in_context(self):
        """Record actions should be filtered in list view context."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        self.client.force_login(self.staff_with_view)

        # Get list view
        url = site.reverse('webshop_product_list')
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that record_actions are present and filtered
        assert 'record_actions' in response.context
        # Should be a list (even if empty)
        assert isinstance(response.context['record_actions'], list)


class TestUpdateViewActionFiltering(RegistrySaveRestoreMixin, TestCase):
    """Test action filtering in UpdateView (Edit) context."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.product = ProductFactory()

        # Create two users: one with view+change, one with view-only
        self.user_with_change = UserFactory(is_staff=True)
        self.user_view_only = UserFactory(is_staff=True)

        # Grant permissions
        content_type = ContentType.objects.get_for_model(Product)
        change_perm = Permission.objects.get(codename='change_product', content_type=content_type)
        view_perm = Permission.objects.get(codename='view_product', content_type=content_type)

        # User with both view and change permissions (can edit)
        self.user_with_change.user_permissions.add(change_perm, view_perm)
        # User with only view permission (can't edit)
        self.user_view_only.user_permissions.add(view_perm)

    def test_update_view_filters_record_actions(self):
        """UpdateView should filter record_actions and add them to context."""
        # Use the already-configured ProductAdmin from webshop
        from examples.webshop.djadmin import ProductAdmin

        site.register(Product, ProductAdmin, override=True)
        self.client.force_login(self.user_with_change)

        # Access update view
        url = site.reverse('webshop_product_edit', kwargs={'pk': self.product.pk})
        response = self.client.get(url)

        assert response.status_code == 200
        # Check that record_actions are in context and filtered
        assert 'record_actions' in response.context
        assert isinstance(response.context['record_actions'], list)

    def test_update_view_hides_view_action_for_change_users(self):
        """
        UpdateView should hide 'View' action for users with change permission.

        The View action has permission: IsStaff & view & ~change
        So users with change permission should NOT see it.
        """
        from examples.webshop.djadmin import ProductAdmin

        site.register(Product, ProductAdmin, override=True)
        self.client.force_login(self.user_with_change)

        # Access update view
        url = site.reverse('webshop_product_edit', kwargs={'pk': self.product.pk})
        response = self.client.get(url)

        assert response.status_code == 200
        filtered_record_actions = response.context['filtered_record_actions']

        # View action should be filtered out (user has change permission)
        view_action_labels = [action.label for action in filtered_record_actions if action.label == 'View']
        assert len(view_action_labels) == 0, 'View action should be hidden for users with change permission'


class TestCheckPermissionMethod(RegistrySaveRestoreMixin, TestCase):
    """Test the check_permission() method implementation details."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.product = ProductFactory()
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.regular_user = UserFactory(is_staff=False)

    def test_check_permission_creates_view_instance(self):
        """check_permission() should create a minimal view instance using cached view_class."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.superuser

        # Get an action
        action = model_admin.general_actions[0]

        # Verify view_class property is used (it should be cached after first access)
        view_class1 = action.view_class
        view_class2 = action.view_class

        # Should be the same class (cached)
        assert view_class1 is view_class2, 'view_class property should be cached'

        # Call check_permission - should use the cached view_class
        action.check_permission(request)

        # Verify it used the same cached view class
        view_class3 = action.view_class
        assert view_class1 is view_class3, 'check_permission should use cached view_class'

    def test_check_permission_calls_test_func(self):
        """check_permission() should call test_func() on the view."""
        site.register(Product, ViewOnlyProductAdmin, override=True)
        model_admin = site.get_model_admins(Product)[0]
        request = self.factory.get('/')
        request.user = self.superuser

        # Get an action
        action = model_admin.general_actions[0]

        # Call check_permission
        result = action.check_permission(request)

        # Verify result (superuser should pass)
        assert result is True, 'check_permission() should return test_func() result'

    def test_check_permission_without_test_func_defaults_to_allow(self):
        """If view has no test_func, check_permission() should default to True."""
        # Create a mock view class without test_func
        from django.views.generic import TemplateView

        class ViewWithoutTestFunc(TemplateView):
            pass

        # Create a custom action that returns this view
        class CustomAction(GeneralActionMixin, BaseAction):
            label = 'Custom'

            def get_template_name(self):
                return 'djadmin/model_list.html'

            def get_view_class(self):
                return ViewWithoutTestFunc

        # Create action instance
        action = CustomAction(Product, None, site)
        request = self.factory.get('/')
        request.user = self.regular_user

        # Call check_permission
        result = action.check_permission(request)

        # Should default to True
        assert result is True, 'check_permission() should default to True if no test_func'


class TestObjectLevelActionFiltering(RegistrySaveRestoreMixin, TestCase):
    """Test object-level permission filtering for actions."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        # Create multiple products with different statuses
        self.active_product = ProductFactory(name='Active Product', status='active')
        self.draft_product = ProductFactory(name='Draft Product', status='draft')
        self.archived_product = ProductFactory(name='Archived Product', status='archived')

        # Create users
        self.superuser = UserFactory(is_superuser=True, is_staff=True)
        self.staff_user = UserFactory(is_staff=True)

        # Grant view and change permissions
        content_type = ContentType.objects.get_for_model(Product)
        view_perm = Permission.objects.get(codename='view_product', content_type=content_type)
        change_perm = Permission.objects.get(codename='change_product', content_type=content_type)
        self.staff_user.user_permissions.add(view_perm, change_perm)

    def test_check_permission_with_object(self):
        """Test that check_permission() accepts and uses obj parameter."""

        # Create a custom permission class that checks object status
        class CanEditActiveOnly:
            def __call__(self, view):
                # If object exists, check its status
                if hasattr(view, 'object') and view.object:
                    return view.object.status == 'active'
                # No object context - allow (model-level permission)
                return True

        # Use the existing webshop ProductAdmin with custom permission
        from examples.webshop.djadmin import ProductAdmin

        class ProductAdminWithObjectPerms(ProductAdmin):
            permission_class = IsStaff() & HasDjangoPermission(perm='change') & CanEditActiveOnly()

        site.register(Product, ProductAdminWithObjectPerms, override=True)
        model_admin = site.get_model_admins(Product)[0]
        # Get the Edit action from record_actions
        action = next((a for a in model_admin.record_actions if a.label == 'Edit'), None)
        assert action is not None, 'Edit action should exist'

        # Create request
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.staff_user

        # Test with active product - should pass
        result_active = action.check_permission(request, obj=self.active_product)
        assert result_active is True, 'Should allow editing active product'

        # Test with draft product - should fail
        result_draft = action.check_permission(request, obj=self.draft_product)
        assert result_draft is False, 'Should deny editing draft product'

        # Test with archived product - should fail
        result_archived = action.check_permission(request, obj=self.archived_product)
        assert result_archived is False, 'Should deny editing archived product'

        # Test without object (model-level) - should pass
        result_no_obj = action.check_permission(request)
        assert result_no_obj is True, 'Should allow model-level access'

    def test_filter_actions_with_object(self):
        """Test that filter_actions() accepts and uses obj parameter."""

        # Create permission class that checks product name
        class CanEditProductsWithA:
            def __call__(self, view):
                if hasattr(view, 'object') and view.object:
                    return 'A' in view.object.name.upper()
                return True

        from examples.webshop.djadmin import ProductAdmin

        class ProductAdminWithNameFilter(ProductAdmin):
            permission_class = IsStaff() & CanEditProductsWithA()

        site.register(Product, ProductAdminWithNameFilter, override=True)
        model_admin = site.get_model_admins(Product)[0]

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.staff_user

        # Filter actions for active product (name has 'A')
        filtered_active = model_admin.filter_actions(model_admin.record_actions, request, obj=self.active_product)
        assert len(filtered_active) > 0, 'Should include actions for product with A in name'

        # Filter actions for draft product (name has 'a')
        filtered_draft = model_admin.filter_actions(model_admin.record_actions, request, obj=self.draft_product)
        assert len(filtered_draft) > 0, 'Should include actions for product with A in name'

        # Create product without 'A' in name
        no_a_product = ProductFactory(name='Product XYZ', status='active')
        filtered_no_a = model_admin.filter_actions(model_admin.record_actions, request, obj=no_a_product)
        assert len(filtered_no_a) == 0, 'Should exclude actions for product without A in name'

    def test_updateview_uses_object_for_filtering(self):
        """Test that UpdateView filters actions based on the current object."""
        # Use existing ProductAdmin and verify that object-level filtering works
        # We'll check that the filtered_record_actions in context varies based on the object
        from examples.webshop.djadmin import ProductAdmin

        site.register(Product, ProductAdmin, override=True)
        self.client.force_login(self.superuser)

        # Access UpdateView for different products - they should all have same actions
        # since we're using default ProductAdmin with no object-level restrictions
        url_active = site.reverse('webshop_product_edit', kwargs={'pk': self.active_product.pk})
        response_active = self.client.get(url_active)

        url_draft = site.reverse('webshop_product_edit', kwargs={'pk': self.draft_product.pk})
        response_draft = self.client.get(url_draft)

        assert response_active.status_code == 200
        assert response_draft.status_code == 200

        # Both should have filtered_record_actions context key
        assert 'filtered_record_actions' in response_active.context
        assert 'filtered_record_actions' in response_draft.context

        # For superuser with default ProductAdmin, both should have same number of actions
        assert len(response_active.context['filtered_record_actions']) == len(
            response_draft.context['filtered_record_actions']
        ), 'Default ProductAdmin should filter same for all objects'

    def test_template_tag_filters_per_row(self):
        """Test that filter_record_actions template tag filters actions per object."""
        from djadmin.templatetags.djadmin_tags import filter_record_actions

        # Permission that only allows archived products
        class CanOnlyViewArchived:
            def __call__(self, view):
                if hasattr(view, 'object') and view.object:
                    return view.object.status == 'archived'
                return True

        from examples.webshop.djadmin import ProductAdmin

        class ProductAdminArchived(ProductAdmin):
            permission_class = IsStaff() & CanOnlyViewArchived()

        site.register(Product, ProductAdminArchived, override=True)
        model_admin = site.get_model_admins(Product)[0]

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.staff_user

        # Create context
        context = {'request': request, 'model_admin': model_admin}

        # Filter for archived product - should include actions
        filtered_archived = filter_record_actions(context, model_admin.record_actions, self.archived_product)
        assert len(filtered_archived) > 0, 'Should show actions for archived product'

        # Filter for active product - should exclude actions
        filtered_active = filter_record_actions(context, model_admin.record_actions, self.active_product)
        assert len(filtered_active) == 0, 'Should hide actions for active product'

        # Filter for draft product - should exclude actions
        filtered_draft = filter_record_actions(context, model_admin.record_actions, self.draft_product)
        assert len(filtered_draft) == 0, 'Should hide actions for draft product'
