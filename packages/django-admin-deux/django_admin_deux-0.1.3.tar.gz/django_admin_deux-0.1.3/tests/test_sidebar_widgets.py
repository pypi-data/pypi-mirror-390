"""Tests for sidebar widget system"""

import pytest

from djadmin import SidebarWidget
from djadmin.factories.base import ViewFactory
from djadmin.plugins import hookimpl, pm
from djadmin.plugins.core.actions import ListAction
from tests.factories import UserFactory


@pytest.fixture
def mock_sidebar_plugin():
    """Plugin that provides a test sidebar widget"""

    class MockSidebarPlugin:
        @hookimpl
        def djadmin_get_sidebar_widgets(self, action):
            return {
                ListAction: [
                    SidebarWidget(
                        template='test/test_widget.html',
                        order=10,
                        identifier='test-widget',
                    ),
                ],
            }

    plugin = MockSidebarPlugin()
    pm.register(plugin)
    yield plugin
    pm.unregister(plugin)


@pytest.fixture
def conditional_sidebar_plugin():
    """Plugin with conditional sidebar widget"""

    class ConditionalSidebarPlugin:
        @hookimpl
        def djadmin_get_sidebar_widgets(self, action):
            return {
                ListAction: [
                    SidebarWidget(
                        template='test/conditional_widget.html',
                        condition=lambda action, request: hasattr(action.model_admin, 'show_widget'),
                        order=20,
                        identifier='conditional-widget',
                    ),
                ],
            }

    plugin = ConditionalSidebarPlugin()
    pm.register(plugin)
    yield plugin
    pm.unregister(plugin)


@pytest.fixture
def context_sidebar_plugin():
    """Plugin with sidebar widget that provides context"""

    class ContextSidebarPlugin:
        @hookimpl
        def djadmin_get_sidebar_widgets(self, action):
            return {
                ListAction: [
                    SidebarWidget(
                        template='test/context_widget.html',
                        context_callback=lambda action, request: {
                            'model_name': action.model.__name__,
                            'count': 42,
                        },
                        order=30,
                        identifier='context-widget',
                    ),
                ],
            }

    plugin = ContextSidebarPlugin()
    pm.register(plugin)
    yield plugin
    pm.unregister(plugin)


class TestSidebarWidgetDataclass:
    """Test SidebarWidget dataclass"""

    def test_should_display_no_condition(self):
        """Widgets without condition should always display"""
        widget = SidebarWidget(template='test.html')
        assert widget.should_display(None, None) is True

    def test_should_display_with_condition_true(self):
        """Widgets with condition returning True should display"""
        widget = SidebarWidget(
            template='test.html',
            condition=lambda action, request: True,
        )
        assert widget.should_display(None, None) is True

    def test_should_display_with_condition_false(self):
        """Widgets with condition returning False should not display"""
        widget = SidebarWidget(
            template='test.html',
            condition=lambda action, request: False,
        )
        assert widget.should_display(None, None) is False

    def test_get_context_no_callback(self):
        """Widgets without context_callback should return empty dict"""
        widget = SidebarWidget(template='test.html')
        assert widget.get_context(None, None) == {}

    def test_get_context_with_callback(self):
        """Widgets with context_callback should return provided context"""
        widget = SidebarWidget(
            template='test.html',
            context_callback=lambda action, request: {'foo': 'bar'},
        )
        assert widget.get_context(None, None) == {'foo': 'bar'}


class TestSidebarWidgetCollection:
    """Test sidebar widget collection in ViewFactory"""

    def test_collect_sidebar_widgets(self, product_admin, mock_sidebar_plugin):
        """ViewFactory should collect sidebar widgets from plugins"""
        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Check that sidebar_widgets attribute was set
        assert hasattr(view_class, 'sidebar_widgets')
        # Should have at least the test widget (may have others from installed plugins)
        assert len(view_class.sidebar_widgets) >= 1
        # Find the test widget by identifier
        test_widget = next((w for w in view_class.sidebar_widgets if w.identifier == 'test-widget'), None)
        assert test_widget is not None
        assert test_widget.template == 'test/test_widget.html'

    def test_multiple_widgets_sorted_by_order(self, product_admin, mock_sidebar_plugin, context_sidebar_plugin):
        """Multiple widgets should be sorted by order attribute"""
        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Should have at least 2 widgets from test fixtures (may have others from installed plugins)
        assert len(view_class.sidebar_widgets) >= 2
        # Find test widgets by identifier
        test_widget = next((w for w in view_class.sidebar_widgets if w.identifier == 'test-widget'), None)
        context_widget = next((w for w in view_class.sidebar_widgets if w.identifier == 'context-widget'), None)
        assert test_widget is not None
        assert context_widget is not None
        # Verify they are sorted by order
        assert test_widget.order == 10
        assert context_widget.order == 30
        # Test widget should come before context widget
        test_idx = view_class.sidebar_widgets.index(test_widget)
        context_idx = view_class.sidebar_widgets.index(context_widget)
        assert test_idx < context_idx

    def test_no_widgets_for_non_matching_actions(self, product_admin, mock_sidebar_plugin):
        """Widgets should only be added to matching action types"""
        from djadmin.plugins.core.actions import AddAction

        action = AddAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # AddAction shouldn't get ListViewAction widgets
        widgets = getattr(view_class, 'sidebar_widgets', [])
        assert len(widgets) == 0


class TestSidebarWidgetsInContext:
    """Test sidebar widgets in view context"""

    def test_widgets_in_context(self, product_admin, mock_sidebar_plugin, rf, db):
        """Sidebar widgets should be available in template context"""
        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        # Create view instance
        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.setup(request)
        view.object_list = view.get_queryset()

        # Get context
        context = view.get_context_data()

        # Check sidebar_widgets in context
        assert 'sidebar_widgets' in context
        assert len(context['sidebar_widgets']) == 1
        assert context['sidebar_widgets'][0]['template'] == 'test/test_widget.html'
        assert context['sidebar_widgets'][0]['identifier'] == 'test-widget'
        assert context['sidebar_widgets'][0]['context'] == {}

    def test_conditional_widget_not_displayed(self, product_admin, conditional_sidebar_plugin, rf, db):
        """Conditional widgets should be filtered based on condition"""
        # ModelAdmin without show_widget attribute
        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.setup(request)
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        # Widget should not be in context (condition failed)
        assert len(context['sidebar_widgets']) == 0

    def test_conditional_widget_displayed(self, product_admin, conditional_sidebar_plugin, rf, db):
        """Conditional widgets should be displayed when condition is met"""
        # Add show_widget attribute to model_admin
        product_admin.show_widget = True

        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.setup(request)
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        # Widget should be in context
        assert len(context['sidebar_widgets']) == 1
        assert context['sidebar_widgets'][0]['identifier'] == 'conditional-widget'

    def test_widget_context_callback(self, product_admin, context_sidebar_plugin, rf, db):
        """Widgets with context_callback should include context data"""
        action = ListAction(
            product_admin.model,
            product_admin,
            product_admin.admin_site,
        )

        factory = ViewFactory()
        view_class = factory.create_view(action)

        request = rf.get('/')
        request.user = UserFactory(is_superuser=True, is_staff=True)  # Add user for permission checks
        view = view_class()
        view.request = request
        view.setup(request)
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        # Check widget context
        assert len(context['sidebar_widgets']) == 1
        widget_data = context['sidebar_widgets'][0]
        assert widget_data['context']['model_name'] == 'Product'
        assert widget_data['context']['count'] == 42
