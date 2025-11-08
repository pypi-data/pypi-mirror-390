"""Test error handling in ViewFactory."""

import pytest

from djadmin.actions.base import BaseAction, GeneralActionMixin
from djadmin.actions.view_mixins import FormViewActionMixin, ListViewActionMixin
from djadmin.factories.base import ViewFactory


class TestViewFactoryErrors:
    """Test ViewFactory handles errors gracefully."""

    def test_action_missing_view_type_mixin(self):
        """Actions without view-type mixin fall back to TemplateView."""

        class InvalidAction(BaseAction):
            """Action with no view-type mixin"""

            label = 'Invalid'
            url_name = 'invalid'

            def get_template_name(self):
                return 'test.html'

        action = InvalidAction(model=None, model_admin=None, admin_site=None)
        factory = ViewFactory()

        # Should succeed with TemplateView as fallback
        view_class = factory.create_view(action)
        assert view_class is not None
        assert hasattr(view_class, 'as_view')

    def test_action_with_multiple_view_type_mixins(self):
        """Action with multiple view-type mixins should use first one found."""

        class MultiMixinAction(GeneralActionMixin, FormViewActionMixin, ListViewActionMixin, BaseAction):
            """Action with multiple view-type mixins"""

            label = 'Multi'
            url_name = 'multi'

        action = MultiMixinAction(model=None, model_admin=None, admin_site=None)
        factory = ViewFactory()

        # Should succeed and use FormView (first view-type mixin in MRO)
        view_class = factory.create_view(action)
        assert view_class is not None

    def test_action_with_invalid_base_class(self):
        """Action returning non-view base class creates invalid view."""

        class InvalidBaseAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Test'
            url_name = 'test'

            def get_base_class(self):
                """Return invalid base class"""
                return str  # Not a view class

            def get_template_name(self):
                return 'test.html'

        action = InvalidBaseAction(model=None, model_admin=None, admin_site=None)
        factory = ViewFactory()

        # Current implementation allows this but creates invalid view
        # (ViewFactory doesn't validate that base_class is a View)
        view_class = factory.create_view(action)
        # The view class is created but is not valid
        assert not hasattr(view_class, 'as_view')

    def test_action_no_label(self):
        """Action without label should raise ValueError."""

        class NoLabelAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            """Action without label attribute"""

            url_name = 'nolabel'
            # No label defined

        # BaseAction.__init__ requires label - should raise ValueError
        with pytest.raises(ValueError, match='must define label'):
            NoLabelAction(model=None, model_admin=None, admin_site=None)

    def test_action_no_url_name(self):
        """Action url_name property requires model."""
        from djadmin import AdminSite, ModelAdmin
        from examples.webshop.models import Product

        class NoUrlAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            """Action without url_name attribute"""

            label = 'Test'
            # No url_name defined - should be auto-generated from class name

            def get_template_name(self):
                return 'test.html'

        # When model is provided, url_name is auto-generated
        action = NoUrlAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should have url_name auto-generated from class name
        assert hasattr(action, 'url_name')
        # 'NoUrlAction' -> 'no_url' (camel to snake case, 'action' removed) -> 'webshop_product_no_url'
        assert action.url_name == 'webshop_product_no_url'

    def test_view_generation_with_empty_plugin_results(self, monkeypatch):
        """ViewFactory should handle empty plugin results gracefully."""
        from djadmin.plugins import pm

        # Mock plugins returning empty results
        def empty_mixins(action):
            return {}

        def empty_attributes(action):
            return {}

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_mixins', empty_mixins)
        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_attributes', empty_attributes)

        class TestAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Test'
            url_name = 'test'

        action = TestAction(model=None, model_admin=None, admin_site=None)
        factory = ViewFactory()

        # Should still create a valid view
        view_class = factory.create_view(action)
        assert view_class is not None
        assert hasattr(view_class, 'as_view')

    def test_action_get_template_names_returns_empty(self):
        """Action with empty template_names should fall back to default."""

        class EmptyTemplateAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Test'
            url_name = 'test'

            def get_template_names(self):
                """Return empty list"""
                return []

        action = EmptyTemplateAction(model=None, model_admin=None, admin_site=None)
        factory = ViewFactory()

        view_class = factory.create_view(action)

        # View should still be created (Django will handle template resolution)
        assert view_class is not None
        assert hasattr(view_class, 'as_view')
