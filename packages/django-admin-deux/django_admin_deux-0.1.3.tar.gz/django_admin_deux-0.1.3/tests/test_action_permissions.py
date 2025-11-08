"""Tests for action-level permissions (django_permission_name, permission_class, test_func)"""

import pytest
from django.contrib.auth import get_user_model

from djadmin.actions import BaseAction
from djadmin.plugins.core.actions import AddAction, DeleteAction, EditAction, ListAction
from djadmin.plugins.permissions import IsAuthenticated

User = get_user_model()


@pytest.mark.django_db
class TestActionDjangoPermissionName:
    """Test that actions have correct django_permission_name attributes"""

    def test_list_view_action_has_view_permission(self, product, admin_site):
        """ListViewAction should have django_permission_name='view'"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = ListAction(product.__class__, model_admin, admin_site)

        assert action.django_permission_name == 'view'

    def test_add_action_has_add_permission(self, product, admin_site):
        """AddAction should have django_permission_name='add'"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = AddAction(product.__class__, model_admin, admin_site)

        assert action.django_permission_name == 'add'

    def test_edit_record_action_has_change_permission(self, product, admin_site):
        """EditRecordAction should have django_permission_name='change'"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = EditAction(product.__class__, model_admin, admin_site)

        assert action.django_permission_name == 'change'

    def test_delete_record_action_has_delete_permission(self, product, admin_site):
        """DeleteRecordAction should have django_permission_name='delete'"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = DeleteAction(product.__class__, model_admin, admin_site)

        assert action.django_permission_name == 'delete'

    def test_base_action_has_default_view_permission(self, product, admin_site):
        """BaseAction should have default django_permission_name='view'"""

        class CustomAction(BaseAction):
            label = 'Custom'

        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = CustomAction(product.__class__, model_admin, admin_site)

        assert action.django_permission_name == 'view'


@pytest.mark.django_db
class TestActionPermissionClass:
    """Test action-level permission_class override"""

    def test_action_accepts_permission_class_in_init(self, product, admin_site):
        """Action should accept permission_class parameter in __init__"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]

        custom_perm = IsAuthenticated()
        action = AddAction(product.__class__, model_admin, admin_site, permission_class=custom_perm)

        assert action.permission_class is custom_perm

    def test_action_without_permission_class_is_none(self, product, admin_site):
        """Action without permission_class should have None"""
        from examples.webshop.djadmin import ProductAdmin

        admin_site.register(product.__class__, ProductAdmin, override=True)
        model_admin = admin_site._registry[product.__class__][0]
        action = AddAction(product.__class__, model_admin, admin_site)

        assert action.permission_class is None


# NOTE: test_func is now provided via closure in the permissions plugin hook
# (djadmin_get_action_view_attributes). Tests for this functionality are in
# tests/plugins/permissions/test_plugin_hooks.py
