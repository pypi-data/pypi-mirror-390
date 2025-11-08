"""
Tests for the feature advertising system.

Tests that Layout.get_features() correctly detects required features
and that plugins can advertise features via the hook system.
"""

from djadmin.layout import Collection, Field, Fieldset, Layout, Row
from djadmin.options import ModelAdmin
from djadmin.plugins.core.actions import AddAction, EditAction
from djadmin.sites import AdminSite
from examples.webshop.models import Category, Product


class TestLayoutGetFeatures:
    """Test Layout.get_features() method"""

    def test_empty_layout_has_no_features(self):
        """Empty layout returns empty set"""
        # This would raise ValueError in __init__, so we can't test it directly
        # Just document expected behavior
        pass

    def test_simple_field_has_no_features(self):
        """Simple Field without advanced attributes has no features"""
        layout = Layout(
            Field('name'),
            Field('price'),
        )
        features = layout.get_features()
        assert features == set()

    def test_field_with_show_if_advertises_conditional_fields(self):
        """Field with show_if advertises 'conditional_fields' feature"""
        layout = Layout(
            Field('name'),
            Field('weight', show_if=".product_type === 'physical'"),
        )
        features = layout.get_features()
        assert 'conditional_fields' in features

    def test_field_with_hide_if_advertises_conditional_fields(self):
        """Field with hide_if advertises 'conditional_fields' feature"""
        layout = Layout(
            Field('name'),
            Field('digital_size', hide_if=".product_type === 'physical'"),
        )
        features = layout.get_features()
        assert 'conditional_fields' in features

    def test_field_with_calculate_advertises_computed_fields(self):
        """Field with calculate advertises 'computed_fields' feature"""
        layout = Layout(
            Field('price'),
            Field('discount'),
            Field('total', calculate='.price * (1 - .discount / 100)'),
        )
        features = layout.get_features()
        assert 'computed_fields' in features

    def test_collection_advertises_collections_and_inlines(self):
        """Collection advertises both 'collections' and 'inlines' features"""
        layout = Layout(
            Field('name'),
            Collection('products', model=Product, fields=['name', 'sku']),
        )
        features = layout.get_features()
        assert 'collections' in features
        assert 'inlines' in features

    def test_multiple_features_detected(self):
        """Layout with multiple feature types detects all"""
        layout = Layout(
            Field('name'),
            Field('weight', show_if=".type === 'physical'"),
            Field('total', calculate='.price * .quantity'),
            Collection('items', model=Product, fields=['name']),
        )
        features = layout.get_features()
        assert 'conditional_fields' in features
        assert 'computed_fields' in features
        assert 'collections' in features
        assert 'inlines' in features

    def test_features_in_fieldset_detected(self):
        """Features inside Fieldset are detected"""
        layout = Layout(
            Fieldset(
                'Details',
                Field('name'),
                Field('weight', show_if=".type === 'physical'"),
            ),
        )
        features = layout.get_features()
        assert 'conditional_fields' in features

    def test_features_in_row_detected(self):
        """Features inside Row are detected"""
        layout = Layout(
            Row(
                Field('price'),
                Field('discount'),
                Field('total', calculate='.price * (1 - .discount / 100)'),
            ),
        )
        features = layout.get_features()
        assert 'computed_fields' in features

    def test_nested_features_detected(self):
        """Features in nested structures are detected"""
        layout = Layout(
            Fieldset(
                'Pricing',
                Row(
                    Field('price'),
                    Field('total', calculate='.price * .quantity'),
                ),
            ),
        )
        features = layout.get_features()
        assert 'computed_fields' in features

    def test_collection_with_layout_detects_nested_features(self):
        """Collection with nested layout detects features recursively"""
        layout = Layout(
            Field('name'),
            Collection(
                'variants',
                model=Product,
                layout=Layout(
                    Field('sku'),
                    Field('discount_price', calculate='.price * 0.9'),
                ),
            ),
        )
        features = layout.get_features()
        assert 'collections' in features
        assert 'computed_fields' in features


class TestActionGetFormFeatures:
    """Test Action.get_form_features() method"""

    def test_action_with_no_layout_has_no_features(self):
        """Action without layout returns empty set"""
        admin_site = AdminSite()

        class CategoryAdmin(ModelAdmin):
            pass

        admin_site.register(Category, CategoryAdmin)
        model_admin = admin_site._registry[Category][0]

        action = AddAction(Category, model_admin, admin_site)
        features = action.get_form_features()
        assert features == set()

    def test_action_with_simple_layout_has_no_features(self):
        """Action with simple layout (no advanced features) returns empty set"""
        admin_site = AdminSite()

        class CategoryAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('description'),
            )

        admin_site.register(Category, CategoryAdmin)
        model_admin = admin_site._registry[Category][0]

        action = AddAction(Category, model_admin, admin_site)
        features = action.get_form_features()
        assert features == set()

    def test_action_detects_layout_features(self):
        """Action detects features from ModelAdmin's layout"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('weight', show_if=".type === 'physical'"),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)
        features = action.get_form_features()
        assert 'conditional_fields' in features

    def test_add_action_detects_features(self):
        """AddAction detects features correctly"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Collection('reviews', model=Category, fields=['name']),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)
        features = action.get_form_features()
        assert 'collections' in features

    def test_edit_action_detects_features(self):
        """EditRecordAction detects features correctly"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('price'),
                Field('total', calculate='.price * .quantity'),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = EditAction(Product, model_admin, admin_site)
        features = action.get_form_features()
        assert 'computed_fields' in features


class TestPluginFeatureAdvertising:
    """Test plugin feature advertising via hooks"""

    def test_plugin_can_add_features_via_hook(self):
        """Plugins can add features via djadmin_get_form_features hook"""
        from djadmin.plugins import hookimpl, pm

        # Create a test plugin that adds custom features
        class TestPlugin:
            @hookimpl
            def djadmin_get_form_features(self, action, model_admin):
                return {'custom_validation', 'special_widget'}

        # Register plugin instance
        plugin_instance = TestPlugin()
        pm.register(plugin_instance)

        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(Field('name'))

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)
        features = action.get_form_features()

        assert 'custom_validation' in features
        assert 'special_widget' in features

        # Cleanup
        pm.unregister(plugin_instance)

    def test_multiple_plugins_can_add_features(self):
        """Multiple plugins can contribute features"""
        from djadmin.plugins import hookimpl, pm

        class PluginA:
            @hookimpl
            def djadmin_get_form_features(self, action, model_admin):
                return {'feature_a'}

        class PluginB:
            @hookimpl
            def djadmin_get_form_features(self, action, model_admin):
                return {'feature_b'}

        # Register plugin instances
        plugin_a = PluginA()
        plugin_b = PluginB()
        pm.register(plugin_a)
        pm.register(plugin_b)

        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(Field('name'))

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)
        features = action.get_form_features()

        assert 'feature_a' in features
        assert 'feature_b' in features

        # Cleanup
        pm.unregister(plugin_a)
        pm.unregister(plugin_b)
