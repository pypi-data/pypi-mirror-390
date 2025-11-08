"""
Tests for dashboard permission-based filtering.

Tests that dashboards hide models/apps where users have no accessible actions,
and raise PermissionDenied when users access apps with no accessible models.
"""

from django.contrib.auth.models import Permission
from django.test import TestCase, override_settings

from djadmin import ModelAdmin, site
from djadmin.plugins.permissions import IsSuperuser
from examples.webshop.factories import CategoryFactory, ProductFactory
from examples.webshop.models import Category, Product
from tests.conftest import RegistrySaveRestoreMixin
from tests.factories import UserFactory


# Dynamic URLconf that regenerates admin URLs on each access
class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestProjectDashboardFiltering(RegistrySaveRestoreMixin, TestCase):
    """Test project dashboard filtering (all apps view)."""

    registry_models = [Product, Category]

    def setUp(self):
        super().setUp()
        # Create test data
        self.products = ProductFactory.create_batch(3)
        self.categories = CategoryFactory.create_batch(2)

        # Create users with different permission levels
        self.superuser = UserFactory(username='superuser', is_superuser=True, is_staff=True)
        self.view_only_user = UserFactory(username='view_only', is_staff=True)
        self.no_permission_user = UserFactory(username='no_perm', is_staff=True)

        # Grant view permission to view_only_user
        view_product = Permission.objects.get(codename='view_product')
        self.view_only_user.user_permissions.add(view_product)

        # Register admins with default permissions
        class ProductAdmin(ModelAdmin):
            pass

        class CategoryAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)
        site.register(Category, CategoryAdmin, override=True)

    def test_superuser_sees_all_apps(self):
        """Superuser should see all registered apps."""
        self.client.force_login(self.superuser)
        response = self.client.get(site.reverse('index'))

        self.assertEqual(response.status_code, 200)
        app_list = response.context['app_list']

        # Should have webshop app
        self.assertGreaterEqual(len(app_list), 1)
        webshop_app = [app for app in app_list if app['name'] == 'webshop'][0]

        # Should have at least Product and Category
        model_admins = webshop_app['model_admins']
        model_names = {ma['model'].__name__ for ma in model_admins}
        self.assertIn('Product', model_names)
        self.assertIn('Category', model_names)

    def test_view_only_user_sees_only_accessible_models(self):
        """User with view permission should only see Product, not Category."""
        self.client.force_login(self.view_only_user)
        response = self.client.get(site.reverse('index'))

        self.assertEqual(response.status_code, 200)
        app_list = response.context['app_list']

        # Should have webshop app
        self.assertGreaterEqual(len(app_list), 1)
        webshop_app = [app for app in app_list if app['name'] == 'webshop'][0]

        # Should have Product (has view permission) but not Category
        model_admins = webshop_app['model_admins']
        model_names = {ma['model'].__name__ for ma in model_admins}
        self.assertIn('Product', model_names)
        self.assertNotIn('Category', model_names)

    def test_no_permission_user_sees_no_apps(self):
        """User with no permissions should see empty dashboard."""
        self.client.force_login(self.no_permission_user)
        response = self.client.get(site.reverse('index'))

        self.assertEqual(response.status_code, 200)
        app_list = response.context['app_list']

        # Should have no apps (all models filtered out)
        self.assertEqual(len(app_list), 0)

    def test_partial_permission_hides_only_inaccessible_models(self):
        """User with permission for one model shouldn't see the other."""
        # Give view permission for Category only
        view_category = Permission.objects.get(codename='view_category')
        self.no_permission_user.user_permissions.add(view_category)
        self.no_permission_user.refresh_from_db()  # Reload to clear permission cache

        self.client.force_login(self.no_permission_user)
        response = self.client.get(site.reverse('index'))

        self.assertEqual(response.status_code, 200)
        app_list = response.context['app_list']

        # Should have webshop app
        self.assertGreaterEqual(len(app_list), 1)
        webshop_app = [app for app in app_list if app['name'] == 'webshop'][0]

        # Should have Category but not Product
        model_admins = webshop_app['model_admins']
        model_names = {ma['model'].__name__ for ma in model_admins}
        self.assertIn('Category', model_names)
        self.assertNotIn('Product', model_names)

    def test_empty_apps_are_hidden(self):
        """Apps with no accessible models should not appear in dashboard."""
        # This test is implicit in test_no_permission_user_sees_no_apps
        # But let's be explicit about it
        self.client.force_login(self.no_permission_user)
        response = self.client.get(site.reverse('index'))

        app_list = response.context['app_list']

        # Webshop app should be filtered out (no accessible models)
        app_names = [app['name'] for app in app_list]
        self.assertNotIn('webshop', app_names)

    def test_model_admin_with_no_accessible_actions_is_hidden(self):
        """ModelAdmin with all actions filtered out should not appear."""
        # Give view_only_user permission for Category so they can still see something
        view_category = Permission.objects.get(codename='view_category')
        self.view_only_user.user_permissions.add(view_category)
        self.view_only_user.refresh_from_db()

        # Unregister and register with custom permission that denies all
        site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            permission_class = IsSuperuser()  # Only superusers

        site.register(Product, ProductAdmin, override=True)

        # Staff user (not superuser) should not see Product
        self.client.force_login(self.view_only_user)
        response = self.client.get(site.reverse('index'))

        app_list = response.context['app_list']

        # Should have webshop app (Category is still accessible)
        self.assertGreaterEqual(len(app_list), 1)
        webshop_app = [app for app in app_list if app['name'] == 'webshop'][0]

        # Should NOT have Product (permission denied)
        model_admins = webshop_app['model_admins']
        model_names = {ma['model'].__name__ for ma in model_admins}
        self.assertNotIn('Product', model_names)


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestAppDashboardFiltering(RegistrySaveRestoreMixin, TestCase):
    """Test app dashboard filtering (single app view)."""

    registry_models = [Product, Category]

    def setUp(self):
        super().setUp()
        # Create test data
        self.products = ProductFactory.create_batch(3)
        self.categories = CategoryFactory.create_batch(2)

        # Create users
        self.superuser = UserFactory(username='superuser', is_superuser=True, is_staff=True)
        self.view_only_user = UserFactory(username='view_only', is_staff=True)
        self.no_permission_user = UserFactory(username='no_perm', is_staff=True)

        # Grant view permission to view_only_user
        view_product = Permission.objects.get(codename='view_product')
        self.view_only_user.user_permissions.add(view_product)

        # Register admins
        class ProductAdmin(ModelAdmin):
            pass

        class CategoryAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)
        site.register(Category, CategoryAdmin, override=True)

    def test_superuser_sees_all_models_in_app(self):
        """Superuser should see all models in app dashboard."""
        self.client.force_login(self.superuser)
        response = self.client.get(site.reverse('webshop_app_index', kwargs={'app_label': 'webshop'}))

        self.assertEqual(response.status_code, 200)
        model_admin_list = response.context['model_admin_list']

        # Should have at least Product and Category
        self.assertGreaterEqual(len(model_admin_list), 2)
        model_names = {ma['model'].__name__ for ma in model_admin_list}
        self.assertIn('Product', model_names)
        self.assertIn('Category', model_names)

    def test_view_only_user_sees_only_accessible_models_in_app(self):
        """User with view permission should only see accessible models."""
        self.client.force_login(self.view_only_user)
        response = self.client.get(site.reverse('webshop_app_index', kwargs={'app_label': 'webshop'}))

        self.assertEqual(response.status_code, 200)
        model_admin_list = response.context['model_admin_list']

        # Should have Product but not Category
        model_names = {ma['model'].__name__ for ma in model_admin_list}
        self.assertIn('Product', model_names)
        self.assertNotIn('Category', model_names)

    def test_no_permission_user_gets_permission_denied(self):
        """User with no accessible models should get PermissionDenied."""
        self.client.force_login(self.no_permission_user)
        response = self.client.get(site.reverse('webshop_app_index', kwargs={'app_label': 'webshop'}))

        # Should get 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_app_dashboard_with_partial_permissions(self):
        """User with permission for some models should see only those."""
        # Give view permission for Category only
        view_category = Permission.objects.get(codename='view_category')
        self.no_permission_user.user_permissions.add(view_category)
        self.no_permission_user.refresh_from_db()  # Reload to clear permission cache

        self.client.force_login(self.no_permission_user)
        response = self.client.get(site.reverse('webshop_app_index', kwargs={'app_label': 'webshop'}))

        self.assertEqual(response.status_code, 200)
        model_admin_list = response.context['model_admin_list']

        # Should have Category but not Product
        model_names = {ma['model'].__name__ for ma in model_admin_list}
        self.assertIn('Category', model_names)
        self.assertNotIn('Product', model_names)

    def test_app_dashboard_respects_model_admin_permissions(self):
        """App dashboard should respect ModelAdmin-level permission overrides."""
        # Give view_only_user permission for Category so they can still see something
        view_category = Permission.objects.get(codename='view_category')
        self.view_only_user.user_permissions.add(view_category)
        self.view_only_user.refresh_from_db()

        # Unregister and register with custom permission
        site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            permission_class = IsSuperuser()  # Only superusers

        site.register(Product, ProductAdmin, override=True)

        # Staff user (not superuser) should only see Category
        self.client.force_login(self.view_only_user)
        response = self.client.get(site.reverse('webshop_app_index', kwargs={'app_label': 'webshop'}))

        self.assertEqual(response.status_code, 200)
        model_admin_list = response.context['model_admin_list']

        # Should NOT have Product (permission denied)
        model_names = {ma['model'].__name__ for ma in model_admin_list}
        self.assertNotIn('Product', model_names)


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestDashboardPermissionEdgeCases(RegistrySaveRestoreMixin, TestCase):
    """Test edge cases for dashboard permission filtering."""

    registry_models = [Product]

    def setUp(self):
        super().setUp()
        self.products = ProductFactory.create_batch(2)
        self.staff_user = UserFactory(username='staff', is_staff=True)

        # Grant all Product permissions
        for perm in ['view', 'add', 'change', 'delete']:
            permission = Permission.objects.get(codename=f'{perm}_product')
            self.staff_user.user_permissions.add(permission)

        # Register only Product (unregister any other models that might be registered)
        from examples.webshop.models import Category, Customer, Order, Review, Tag

        for model in [Category, Customer, Order, Review, Tag]:
            if model in site._registry:
                site.unregister(model)

        # Register Product with default permissions
        class ProductAdmin(ModelAdmin):
            pass

        site.register(Product, ProductAdmin, override=True)

    def test_dashboard_with_permission_class_none(self):
        """ModelAdmin with permission_class=None should be visible to all staff."""
        site.unregister(Product)

        class ProductAdmin(ModelAdmin):
            permission_class = None  # No permission check

        site.register(Product, ProductAdmin, override=True)

        self.client.force_login(self.staff_user)
        response = self.client.get(site.reverse('index'))

        self.assertEqual(response.status_code, 200)
        app_list = response.context['app_list']

        # Should see webshop app with exactly Product
        self.assertEqual(len(app_list), 1)
        self.assertEqual(app_list[0]['name'], 'webshop')
        self.assertEqual(len(app_list[0]['model_admins']), 1)
        self.assertEqual(app_list[0]['model_admins'][0]['model'].__name__, 'Product')

    def test_dashboard_shows_models_with_any_accessible_action(self):
        """ModelAdmin should appear if user has permission for ANY action."""
        # Remove all permissions except view
        self.staff_user.user_permissions.clear()
        view_product = Permission.objects.get(codename='view_product')
        self.staff_user.user_permissions.add(view_product)
        self.staff_user.refresh_from_db()  # Reload to clear permission cache

        self.client.force_login(self.staff_user)
        response = self.client.get(site.reverse('index'))

        app_list = response.context['app_list']

        # Should see webshop app with exactly Product (has view permission)
        self.assertEqual(len(app_list), 1)
        self.assertEqual(app_list[0]['name'], 'webshop')
        self.assertEqual(len(app_list[0]['model_admins']), 1)
        self.assertEqual(app_list[0]['model_admins'][0]['model'].__name__, 'Product')

        # General actions should be filtered (only view action visible)
        general_actions = app_list[0]['model_admins'][0]['general_actions']
        action_labels = [a['label'] for a in general_actions]

        # Should only have actions user has permission for
        # (Specific actions depend on which ones check 'view' permission)
        self.assertTrue(len(action_labels) > 0, 'Should have at least one accessible action')

    def test_multiple_model_admins_for_same_model(self):
        """When multiple ModelAdmins registered, show only accessible ones."""

        # Register second admin with different permissions
        class RestrictedProductAdmin(ModelAdmin):
            permission_class = IsSuperuser()

        site.register(Product, RestrictedProductAdmin)  # Appends to list

        self.client.force_login(self.staff_user)
        response = self.client.get(site.reverse('index'))

        app_list = response.context['app_list']

        # Should see webshop app with exactly one accessible Product admin
        self.assertEqual(len(app_list), 1)
        self.assertEqual(app_list[0]['name'], 'webshop')

        # Count Product admins
        product_admins = [ma for ma in app_list[0]['model_admins'] if ma['model'] == Product]

        # Should only see one ProductAdmin (the accessible one, not the restricted one)
        self.assertEqual(len(product_admins), 1)
        # Should NOT have "(RestrictedProductAdmin)" in display name
        self.assertNotIn('RestrictedProductAdmin', product_admins[0]['display_name'])
