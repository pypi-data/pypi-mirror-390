"""Test action edge cases."""

from djadmin import AdminSite, ModelAdmin
from djadmin.actions.base import BaseAction, BulkActionMixin, GeneralActionMixin
from djadmin.actions.view_mixins import FormViewActionMixin, TemplateViewActionMixin
from examples.webshop.models import Product


class TestActionEdgeCases:
    """Test edge cases in action handling."""

    def test_action_with_default_attributes(self):
        """Action with default attributes should work."""

        class MinimalAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Minimal'  # Required attribute
            _url_name = 'minimal'

            def get_template_name(self):
                return 'test.html'

        action = MinimalAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should have default values for optional attributes
        assert action.label == 'Minimal'
        assert hasattr(action, 'url_name')
        assert hasattr(action, 'css_class')
        assert action.css_class == ''  # Default empty string
        assert hasattr(action, 'icon')
        assert action.icon is None  # Default None

    def test_action_with_empty_strings(self):
        """Action with empty string attributes should work."""

        class EmptyAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = ''
            url_name = ''
            css_class = ''
            icon = ''

        action = EmptyAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should preserve empty strings
        assert action.label == ''
        assert action.url_name == ''
        assert action.css_class == ''
        assert action.icon == ''

    def test_action_with_unicode_label(self):
        """Action with unicode label should work."""

        class UnicodeAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Añadir 新增 إضافة'
            url_name = 'unicode_action'

        action = UnicodeAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        assert action.label == 'Añadir 新增 إضافة'

    def test_action_with_very_long_label(self):
        """Action with very long label should work."""

        class LongLabelAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'A' * 1000
            url_name = 'long'

        action = LongLabelAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        assert len(action.label) == 1000

    def test_action_with_special_characters_in_url_name(self):
        """Action with special characters in url_name should work or fail gracefully."""

        class SpecialUrlAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Special'
            url_name = 'action-with_dots.and-dashes'

        action = SpecialUrlAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should preserve url_name (Django URL routing will validate)
        assert action.url_name == 'action-with_dots.and-dashes'

    def test_action_http_method_variations(self):
        """Action http_method should accept different values."""

        class GetAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'GET Action'
            url_name = 'get'
            http_method = 'GET'

        class PostAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'POST Action'
            url_name = 'post'
            http_method = 'POST'

        action1 = GetAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())
        action2 = PostAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        assert action1.http_method == 'GET'
        assert action2.http_method == 'POST'

    def test_action_with_multiple_inheritance(self):
        """Action with multiple base mixins should work."""

        class MultiInheritAction(GeneralActionMixin, BulkActionMixin, FormViewActionMixin, BaseAction):
            label = 'Multi'
            url_name = 'multi'

        action = MultiInheritAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should work (MRO will determine behavior)
        assert action is not None

    def test_bulk_action_with_queryset_method(self):
        """Bulk action with custom get_queryset should work."""

        class CustomQuerysetBulkAction(BulkActionMixin, TemplateViewActionMixin, BaseAction):
            label = 'Custom Bulk'
            url_name = 'custom_bulk'

            def get_queryset(self, request):
                """Custom queryset filtering"""
                qs = super().get_queryset(request)
                return qs.filter(is_active=True)

        action = CustomQuerysetBulkAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        assert hasattr(action, 'get_queryset')

    def test_action_with_custom_template_name(self):
        """Action with custom template should work."""

        class CustomTemplateAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Custom Template'
            url_name = 'custom_template'

            def get_template_names(self):
                return ['custom/my_action.html']

        action = CustomTemplateAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        templates = action.get_template_names()
        assert 'custom/my_action.html' in templates

    def test_action_with_dynamic_attributes(self):
        """Action with dynamically computed attributes should work."""

        class DynamicAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            @property
            def label(self):
                return f'Add {self.model._meta.verbose_name}'

            url_name = 'dynamic'

        action = DynamicAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Should compute label dynamically
        assert 'Product' in action.label or 'product' in action.label.lower()

    def test_action_with_none_model(self):
        """Action with None model should handle gracefully."""

        class NoModelAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'No Model'
            url_name = 'nomodel'

        action = NoModelAction(None, None, AdminSite())

        # Should create action (methods may fail when accessed)
        assert action.model is None
        assert action.model_admin is None

    def test_action_context_data_with_extra_kwargs(self):
        """Action get_context_data with extra kwargs should work."""

        class ExtraContextAction(GeneralActionMixin, FormViewActionMixin, BaseAction):
            label = 'Extra'
            url_name = 'extra'

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['custom_key'] = 'custom_value'
                return context

        action = ExtraContextAction(Product, ModelAdmin(Product, AdminSite()), AdminSite())

        # Method should be callable
        assert callable(action.get_context_data)
