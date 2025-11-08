"""
Tests for layout feature validation.

Tests that the feature validation system correctly raises errors when
required features (collections, conditional fields, etc.) are used without
the necessary plugins installed.
"""

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from djadmin.layout import Collection, Field, Fieldset, Layout, Row
from djadmin.options import ModelAdmin
from djadmin.plugins import pm
from djadmin.plugins.core.actions import AddAction, EditAction
from djadmin.sites import AdminSite
from examples.webshop.models import Category, Product


# Override settings to exclude djadmin_formset plugin
@override_settings(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        'debug_toolbar',
        'django_filters',
        'formset',  # Keep formset, just not djadmin_formset
        'djadmin.plugins.theme',
        'djadmin',
        'djadmin_filters',
        # 'djadmin_formset' - EXCLUDED for these tests
        'examples.webshop',
    ]
)
class TestValidateFeatures(TestCase):
    """Test validate_features() method"""

    def setUp(self):
        """Unregister all plugins before settings override"""
        # Store all currently registered plugins
        self._saved_plugins = {}
        for name, plugin in list(pm.list_name_plugin()):
            self._saved_plugins[name] = plugin
            pm.unregister(plugin)

    def tearDown(self):
        """Re-register all plugins after test"""
        # Unregister any plugins added during test
        for name, plugin in list(pm.list_name_plugin()):
            if name not in self._saved_plugins:
                pm.unregister(plugin)

        # Re-register original plugins
        for name, plugin in self._saved_plugins.items():
            if not pm.is_registered(name):
                pm.register(plugin)

    def test_simple_layout_validates_successfully(self):
        """Simple layout without advanced features validates"""
        admin_site = AdminSite()

        class CategoryAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('description'),
            )

        admin_site.register(Category, CategoryAdmin)
        model_admin = admin_site._registry[Category][0]

        action = AddAction(Category, model_admin, admin_site)

        # Should not raise
        action.validate_features()

    def test_no_layout_validates_successfully(self):
        """No layout validates successfully"""
        admin_site = AdminSite()

        class CategoryAdmin(ModelAdmin):
            pass

        admin_site.register(Category, CategoryAdmin)
        model_admin = admin_site._registry[Category][0]

        action = AddAction(Category, model_admin, admin_site)

        # Should not raise
        action.validate_features()

    def test_collection_without_plugin_raises_error(self):
        """Collection without djadmin-formset plugin raises ImproperlyConfigured"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Collection('variants', model=Category, fields=['name']),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured) as cm:
            action.validate_features()

        error_msg = str(cm.exception).lower()
        self.assertIn('inline editing', error_msg)
        self.assertIn('djadmin-formset', error_msg)
        self.assertIn('pip install', error_msg)

    def test_show_if_without_plugin_raises_error(self):
        """show_if without djadmin-formset plugin raises ImproperlyConfigured"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('weight', show_if=".type === 'physical'"),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured) as cm:
            action.validate_features()

        error_msg = str(cm.exception).lower()
        self.assertIn('conditional fields', error_msg)
        self.assertIn('djadmin-formset', error_msg)

    def test_hide_if_without_plugin_raises_error(self):
        """hide_if without djadmin-formset plugin raises ImproperlyConfigured"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('size', hide_if=".type === 'service'"),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured) as cm:
            action.validate_features()

        error_msg = str(cm.exception).lower()
        self.assertIn('conditional fields', error_msg)
        self.assertIn('djadmin-formset', error_msg)

    def test_calculate_without_plugin_raises_error(self):
        """calculate without djadmin-formset plugin raises ImproperlyConfigured"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('price'),
                Field('discount'),
                Field('total', calculate='.price * (1 - .discount / 100)'),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured) as cm:
            action.validate_features()

        error_msg = str(cm.exception).lower()
        self.assertIn('computed fields', error_msg)
        self.assertIn('djadmin-formset', error_msg)

    def test_multiple_features_without_plugin_shows_all_errors(self):
        """Multiple missing features are all mentioned in error message"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('weight', show_if=".type === 'physical'"),
                Field('total', calculate='.price * .quantity'),
                Collection('variants', model=Category, fields=['name']),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured) as cm:
            action.validate_features()

        error_message = str(cm.exception).lower()
        # Should mention inline editing (collections)
        self.assertTrue('inline editing' in error_message or 'collection' in error_message)

    def test_nested_collection_without_plugin_raises_error(self):
        """Nested Collection in Fieldset without plugin raises error"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Fieldset(
                    'Details',
                    Field('name'),
                    Collection('variants', model=Category, fields=['name']),
                ),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured):
            action.validate_features()

    def test_conditional_field_in_row_without_plugin_raises_error(self):
        """Conditional field in Row without plugin raises error"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Row(
                    Field('price'),
                    Field('discount', show_if='.has_discount'),
                ),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        with self.assertRaises(ImproperlyConfigured):
            action.validate_features()


@override_settings(
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        'debug_toolbar',
        'django_filters',
        'formset',  # Keep formset, just not djadmin_formset
        'djadmin.plugins.theme',
        'djadmin',
        'djadmin_filters',
        # 'djadmin_formset' - EXCLUDED for these tests
        'examples.webshop',
    ]
)
class TestValidationInGetFormClass(TestCase):
    """Test that validation is called in get_form_class()"""

    def setUp(self):
        """Unregister all plugins before settings override"""
        # Store all currently registered plugins
        self._saved_plugins = {}
        for name, plugin in list(pm.list_name_plugin()):
            self._saved_plugins[name] = plugin
            pm.unregister(plugin)

    def tearDown(self):
        """Re-register all plugins after test"""
        # Unregister any plugins added during test
        for name, plugin in list(pm.list_name_plugin()):
            if name not in self._saved_plugins:
                pm.unregister(plugin)

        # Re-register original plugins
        for name, plugin in self._saved_plugins.items():
            if not pm.is_registered(name):
                pm.register(plugin)

    def test_add_action_validates_on_get_form_class(self):
        """AddAction.get_form_class() calls validate_features()"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Collection('variants', model=Category, fields=['name']),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        # get_form_class should trigger validation
        with self.assertRaises(ImproperlyConfigured) as cm:
            action.get_form_class()

        # Verify error mentions the feature
        self.assertIn('djadmin-formset', str(cm.exception).lower())

    def test_edit_action_validates_on_get_form_class(self):
        """EditRecordAction.get_form_class() calls validate_features()"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('price'),
                Field('total', calculate='.price * .quantity'),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = EditAction(Product, model_admin, admin_site)

        # get_form_class should trigger validation
        with self.assertRaises(ImproperlyConfigured) as cm:
            action.get_form_class()

        # Verify error mentions the feature
        self.assertIn('djadmin-formset', str(cm.exception).lower())

    def test_validation_happens_before_form_building(self):
        """Validation happens before FormBuilder is called"""
        admin_site = AdminSite()

        class ProductAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('weight', show_if=".type === 'physical'"),
            )

        admin_site.register(Product, ProductAdmin)
        model_admin = admin_site._registry[Product][0]

        action = AddAction(Product, model_admin, admin_site)

        # Should raise during validation, not during form building
        with self.assertRaises(ImproperlyConfigured) as cm:
            action.get_form_class()

        # Error should be about missing plugin, not form building
        self.assertIn('djadmin-formset', str(cm.exception))
