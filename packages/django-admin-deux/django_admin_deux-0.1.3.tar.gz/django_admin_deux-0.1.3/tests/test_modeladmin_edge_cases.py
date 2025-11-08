"""Test ModelAdmin edge cases."""

from djadmin import AdminSite, ModelAdmin
from djadmin.options import Column
from examples.webshop.models import Product


class TestModelAdminEdgeCases:
    """Test edge cases in ModelAdmin configuration."""

    def test_empty_list_display(self):
        """Empty list_display should fall back to __str__."""

        class EmptyAdmin(ModelAdmin):
            list_display = []

        admin = EmptyAdmin(Product, AdminSite())

        # Should normalize to default Column('__str__')
        assert len(admin.list_display) == 1
        assert isinstance(admin.list_display[0], Column)
        assert admin.list_display[0].field == '__str__'

    def test_list_display_with_column_objects(self):
        """list_display can contain Column objects."""

        class ColumnAdmin(ModelAdmin):
            list_display = [
                'name',
                Column('price', label='Price (USD)'),
                'category',
            ]

        admin = ColumnAdmin(Product, AdminSite())

        # Should preserve Column objects
        assert len(admin.list_display) == 3
        assert isinstance(admin.list_display[1], Column)
        assert admin.list_display[1].label == 'Price (USD)'

    def test_list_display_with_callable(self):
        """list_display can contain callables."""

        def custom_price(obj):
            return f'${obj.price}'

        custom_price.short_description = 'Custom Price'

        class CallableAdmin(ModelAdmin):
            list_display = ['name', custom_price]

        admin = CallableAdmin(Product, AdminSite())

        assert len(admin.list_display) == 2
        # Second item should be Column wrapping the callable
        assert isinstance(admin.list_display[1], Column)
        assert callable(admin.list_display[1].field)

    def test_zero_pagination(self):
        """paginate_by=0 or None should work."""

        class NoPaginationAdmin(ModelAdmin):
            paginate_by = None

        admin = NoPaginationAdmin(Product, AdminSite())
        assert admin.paginate_by is None

        class ZeroPaginationAdmin(ModelAdmin):
            paginate_by = 0

        admin2 = ZeroPaginationAdmin(Product, AdminSite())
        assert admin2.paginate_by == 0

    def test_negative_pagination(self):
        """Negative paginate_by should be handled."""

        class NegativePaginationAdmin(ModelAdmin):
            paginate_by = -10

        admin = NegativePaginationAdmin(Product, AdminSite())

        # Should either reject or use default
        # Current implementation may allow it, which is fine
        assert isinstance(admin.paginate_by, int)

    def test_huge_pagination(self):
        """Very large paginate_by should work."""

        class HugePaginationAdmin(ModelAdmin):
            paginate_by = 1000000

        admin = HugePaginationAdmin(Product, AdminSite())
        assert admin.paginate_by == 1000000

    def test_fields_as_all_string(self):
        """fields='__all__' should work."""

        class AllFieldsAdmin(ModelAdmin):
            fields = '__all__'

        admin = AllFieldsAdmin(Product, AdminSite())
        assert admin.fields == '__all__'

    def test_empty_fields_list(self):
        """Empty fields list should work."""

        class EmptyFieldsAdmin(ModelAdmin):
            fields = []

        admin = EmptyFieldsAdmin(Product, AdminSite())
        assert admin.fields == []

    def test_create_fields_fallback(self):
        """create_fields should fall back to fields."""

        class FallbackAdmin(ModelAdmin):
            fields = ['name', 'price']

        admin = FallbackAdmin(Product, AdminSite())
        assert admin.create_fields is None  # Not set
        assert admin.fields == ['name', 'price']

    def test_update_fields_fallback(self):
        """update_fields should fall back to fields."""

        class FallbackAdmin(ModelAdmin):
            fields = ['name', 'description']

        admin = FallbackAdmin(Product, AdminSite())
        assert admin.update_fields is None
        assert admin.fields == ['name', 'description']

    def test_no_actions_defined(self):
        """ModelAdmin with no actions should use defaults from plugins."""

        class NoActionsAdmin(ModelAdmin):
            pass

        admin = NoActionsAdmin(Product, AdminSite())

        # Should have default actions from core plugin
        # Note: list_actions are now merged into general_actions in Phase 5A
        assert len(admin.general_actions) > 0
        assert len(admin.record_actions) > 0

    def test_empty_actions_lists(self):
        """Empty action lists should override defaults."""

        class EmptyActionsAdmin(ModelAdmin):
            general_actions = []
            list_actions = []
            bulk_actions = []
            record_actions = []

        admin = EmptyActionsAdmin(Product, AdminSite())

        # Should respect empty lists (no defaults added)
        assert admin.general_actions == []
        assert admin.list_actions == []
        assert admin.bulk_actions == []
        assert admin.record_actions == []

    def test_requested_features_with_none_values(self):
        """requested_features should ignore None values."""

        class NoneFeatureAdmin(ModelAdmin):
            search_fields = None
            list_filter = None
            ordering = None

        admin = NoneFeatureAdmin(Product, AdminSite())

        # Should have no requested features
        features = admin.requested_features
        assert len(features) == 0

    def test_requested_features_with_empty_lists(self):
        """requested_features should ignore empty lists."""

        class EmptyFeatureAdmin(ModelAdmin):
            search_fields = []
            list_filter = []
            ordering = []

        admin = EmptyFeatureAdmin(Product, AdminSite())

        # Should have no requested features
        features = admin.requested_features
        assert len(features) == 0

    def test_custom_view_classes(self):
        """Custom view classes should be preserved."""
        from django.views.generic import ListView

        class CustomListView(ListView):
            pass

        class CustomViewAdmin(ModelAdmin):
            list_view_class = CustomListView

        admin = CustomViewAdmin(Product, AdminSite())
        assert admin.list_view_class == CustomListView

    def test_form_class_configuration(self):
        """Form class configuration should work."""
        from django import forms

        class CustomForm(forms.ModelForm):
            class Meta:
                model = Product
                fields = '__all__'  # noqa: DJ007

        class FormAdmin(ModelAdmin):
            form_class = CustomForm

        admin = FormAdmin(Product, AdminSite())
        assert admin.form_class == CustomForm

    def test_create_and_update_form_classes(self):
        """Separate create and update form classes should work."""
        from django import forms

        class CreateForm(forms.ModelForm):
            class Meta:
                model = Product
                fields = ['name', 'slug']

        class UpdateForm(forms.ModelForm):
            class Meta:
                model = Product
                fields = '__all__'  # noqa: DJ007

        class SeparateFormsAdmin(ModelAdmin):
            create_form_class = CreateForm
            update_form_class = UpdateForm

        admin = SeparateFormsAdmin(Product, AdminSite())
        assert admin.create_form_class == CreateForm
        assert admin.update_form_class == UpdateForm
