"""Tests for action-centric ViewFactory"""

from django.views.generic import FormView, ListView, TemplateView

from djadmin import ModelAdmin
from djadmin.actions.base import BaseAction
from djadmin.actions.view_mixins import FormViewActionMixin, ListViewActionMixin
from djadmin.factories.base import ViewFactory
from djadmin.plugins.core.actions import ListAction
from examples.webshop.models import Product
from tests.factories import UserFactory


class TestViewFactory:
    """Test ViewFactory with action-centric architecture"""

    def test_create_view_from_list_action(self, admin_site):
        """Factory should create ListView from ListViewAction"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        assert view_class is not None
        assert issubclass(view_class, ListView)
        assert view_class.action == action
        assert view_class.model == Product
        assert view_class.model_admin == model_admin
        assert view_class.admin_site == admin_site

    def test_get_base_class_from_action(self, admin_site):
        """Factory should get base class from action's view mixin"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        class TestAction(FormViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        action = TestAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        assert issubclass(view_class, FormView)

    def test_get_base_class_from_plugin(self, admin_site, monkeypatch):
        """Factory should use plugin-provided base class override"""
        from djadmin.plugins import pm

        class CustomListView(ListView):
            custom_attr = True

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        def mock_base_class(action):
            return [{TestAction: CustomListView}]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_base_class', mock_base_class)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        assert issubclass(view_class, CustomListView)
        assert hasattr(view_class, 'custom_attr')

    def test_get_mixins_from_plugin(self, admin_site, monkeypatch):
        """Factory should include mixins from plugin registry"""
        from djadmin.plugins import pm

        class Mixin1:
            mixin1_attr = 'value1'

        class Mixin2:
            mixin2_attr = 'value2'

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        def mock_mixins(action):
            return [{ListViewActionMixin: [Mixin1, Mixin2]}]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_mixins', mock_mixins)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Check MRO includes mixins
        assert Mixin1 in view_class.__mro__
        assert Mixin2 in view_class.__mro__

        # Check attributes are accessible
        assert hasattr(view_class, 'mixin1_attr')
        assert hasattr(view_class, 'mixin2_attr')

    def test_isinstance_matching_for_mixins(self, admin_site, monkeypatch):
        """Factory should match actions using isinstance() for mixin inheritance"""
        from djadmin.plugins import pm

        class SpecialMixin:
            special_attr = True

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        # Plugin registers mixin for ListViewActionMixin base class
        def mock_mixins(action):
            return [{ListViewActionMixin: [SpecialMixin]}]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_mixins', mock_mixins)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Should match because TestAction is instance of ListViewActionMixin
        assert SpecialMixin in view_class.__mro__
        assert hasattr(view_class, 'special_attr')

    def test_get_attributes_from_plugin(self, admin_site, monkeypatch):
        """Factory should include attributes from plugin registry"""
        from djadmin.plugins import pm

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        def mock_attributes(action):
            return [{ListViewActionMixin: {'custom_attr': 'value', 'paginate_by': 50}}]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_attributes', mock_attributes)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        assert hasattr(view_class, 'custom_attr')
        assert view_class.custom_attr == 'value'
        assert view_class.paginate_by == 50

    def test_view_class_name_generation(self, admin_site):
        """Generated view class should have descriptive name"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Should be: {ModelName}{ActionName}View
        # ListViewAction -> ListView
        assert view_class.__name__ == 'ProductListView'

    def test_get_context_data_includes_action(self, admin_site, db, rf):
        """View should include action in context"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.kwargs = {}
        view.object_list = Product.objects.none()

        context = view.get_context_data()

        assert 'action' in context
        assert context['action'] == action
        assert 'opts' in context
        assert context['opts'] == Product._meta
        assert 'model_admin' in context
        assert context['model_admin'] == model_admin
        assert 'admin_site' in context
        assert context['admin_site'] == admin_site

    def test_get_template_names_from_action(self, admin_site):
        """View should get template names from action"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        view = view_class()
        templates = view.get_template_names()

        # ListViewAction returns list of templates
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert 'djadmin/webshop/product_list.html' in templates
        assert 'djadmin/actions/list.html' in templates

    def test_assets_in_context(self, admin_site, db, rf, monkeypatch):
        """Context should include assets from plugins"""
        from djadmin.plugins import pm

        def mock_assets(action):
            return [{ListViewActionMixin: {'css': ['test.css'], 'js': ['test.js']}}]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_assets', mock_assets)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = ListAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.kwargs = {}
        view.object_list = Product.objects.none()

        context = view.get_context_data()

        assert 'assets' in context
        # Assets are CSSAsset/JSAsset objects, not strings
        assert any(asset.href == 'test.css' for asset in context['assets']['css'])
        assert any(asset.src == 'test.js' for asset in context['assets']['js'])

    def test_multiple_plugins_contribute_mixins(self, admin_site, monkeypatch):
        """Multiple plugins should be able to contribute mixins"""
        from djadmin.plugins import pm

        class Plugin1Mixin:
            plugin1_attr = True

        class Plugin2Mixin:
            plugin2_attr = True

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        def mock_mixins(action):
            # Simulate multiple plugins returning registries
            return [
                {ListViewActionMixin: [Plugin1Mixin]},
                {ListViewActionMixin: [Plugin2Mixin]},
            ]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_mixins', mock_mixins)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Both mixins should be included
        assert Plugin1Mixin in view_class.__mro__
        assert Plugin2Mixin in view_class.__mro__

    def test_plugin_attributes_override(self, admin_site, monkeypatch):
        """Later plugin attributes should override earlier ones"""
        from djadmin.plugins import pm

        class TestAction(ListViewActionMixin, BaseAction):
            label = 'Test'

            def get_template_name(self):
                return 'test.html'

        def mock_attributes(action):
            return [
                {ListViewActionMixin: {'custom_attr': 'first'}},
                {ListViewActionMixin: {'custom_attr': 'second'}},
            ]

        monkeypatch.setattr(pm.hook, 'djadmin_get_action_view_attributes', mock_attributes)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Later plugin should win
        assert view_class.custom_attr == 'second'

    def test_fallback_to_template_view(self, admin_site):
        """Factory should fall back to TemplateView if no base_class found"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        class PlainAction(BaseAction):
            label = 'Plain'

            def get_template_name(self):
                return 'test.html'

        action = PlainAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Should fall back to TemplateView
        assert issubclass(view_class, TemplateView)

    def test_custom_action_with_form_view_mixin(self, admin_site):
        """Custom action with FormViewActionMixin should generate FormView"""
        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        class CustomFormAction(FormViewActionMixin, BaseAction):
            label = 'Custom Form'

            def get_template_name(self):
                return 'custom_form.html'

        action = CustomFormAction(Product, model_admin, admin_site)
        factory = ViewFactory()
        view_class = factory.create_view(action)

        assert issubclass(view_class, FormView)
        assert view_class.__name__ == 'ProductCustomFormView'
