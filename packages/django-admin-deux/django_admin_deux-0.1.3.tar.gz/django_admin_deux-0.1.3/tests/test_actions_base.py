"""Tests for action base classes"""

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory

from djadmin import ModelAdmin
from djadmin.actions import (
    BaseAction,
    BulkActionMixin,
    ConfirmationActionMixin,
    FormActionMixin,
    GeneralActionMixin,
    RecordActionMixin,
)
from examples.webshop.models import Product

User = get_user_model()


class TestBaseAction:
    """Test BaseAction functionality"""

    def test_action_requires_label(self, admin_site):
        """Action without label should raise ValueError"""

        class NoLabelAction(GeneralActionMixin, BaseAction):
            pass

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        with pytest.raises(ValueError, match='must define label'):
            NoLabelAction(Product, model_admin, admin_site)

    def test_action_with_label(self, admin_site):
        """Action with label should initialize"""

        class TestAction(GeneralActionMixin, BaseAction):
            label = 'Test Action'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]

        action = TestAction(Product, model_admin, admin_site)

        assert action.label == 'Test Action'
        assert action.model == Product
        assert action.model_admin == model_admin
        assert action.admin_site == admin_site

    def test_get_url_name(self, admin_site):
        """URL name should be generated from model and action class name"""

        class TestAction(GeneralActionMixin, BaseAction):
            label = 'Test'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        url_name = action.get_url_name()
        assert url_name == 'webshop_product_test'


class TestGeneralActionMixin:
    """Test GeneralActionMixin functionality"""

    def test_list_action_type(self, admin_site):
        """GeneralActionMixin should set action_type"""

        class TestAction(GeneralActionMixin, BaseAction):
            label = 'Test'

            def execute(self, request, **kwargs):
                return HttpResponse('executed')

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.action_type == 'general'


class TestBulkActionMixin:
    """Test BulkActionMixin functionality"""

    def test_bulk_action_type(self, admin_site):
        """BulkActionMixin should set action_type"""

        class TestAction(BulkActionMixin, BaseAction):
            label = 'Test'

            def execute(self, request, queryset, **kwargs):
                return HttpResponse('executed')

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.action_type == 'bulk'

    def test_bulk_action_with_queryset(self, admin_site, product_factory, db):
        """BulkAction should receive queryset"""

        class TestAction(BulkActionMixin, BaseAction):
            label = 'Test'

            def execute(self, request, queryset, **kwargs):
                return HttpResponse(f'Count: {queryset.count()}')

        # Create test data
        product_factory.create_batch(5)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = RequestFactory()
        request = factory.get('/')

        queryset = Product.objects.all()
        response = action.execute(request, queryset)

        assert b'Count: 5' in response.content


class TestRecordActionMixin:
    """Test RecordActionMixin functionality"""

    def test_record_action_type(self, admin_site):
        """RecordActionMixin should set action_type"""

        class TestAction(RecordActionMixin, BaseAction):
            label = 'Test'

            def execute(self, request, obj, **kwargs):
                return HttpResponse('executed')

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.action_type == 'record'

    def test_record_action_with_object(self, admin_site, product_factory, db):
        """RecordAction should receive object"""

        class TestAction(RecordActionMixin, BaseAction):
            label = 'Test'

            def execute(self, request, obj, **kwargs):
                return HttpResponse(f'Object: {obj.name}')

        product = product_factory(name='Test Product')

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = RequestFactory()
        request = factory.get('/')

        response = action.execute(request, product)

        assert b'Object: Test Product' in response.content


class TestFormActionMixin:
    """Test FormActionMixin functionality"""

    def test_form_action_requires_form_class(self, admin_site):
        """FormActionMixin should require form_class"""

        class TestAction(GeneralActionMixin, FormActionMixin, BaseAction):
            label = 'Test'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        with pytest.raises(ValueError, match='must define form_class'):
            action.get_form_class()

    def test_get_template_name_default(self, admin_site):
        """Should return default modal template"""
        from django import forms

        class TestForm(forms.Form):
            test_field = forms.CharField()

        class TestAction(GeneralActionMixin, FormActionMixin, BaseAction):
            label = 'Test'
            form_class = TestForm

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.get_template_name() == 'djadmin/actions/form_modal.html'

    def test_get_template_name_custom(self, admin_site):
        """Should return custom template if set"""
        from django import forms

        class TestForm(forms.Form):
            test_field = forms.CharField()

        class TestAction(GeneralActionMixin, FormActionMixin, BaseAction):
            label = 'Test'
            form_class = TestForm
            template_name = 'custom/form.html'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.get_template_name() == 'custom/form.html'

    def test_form_valid_required(self, admin_site):
        """FormActionMixin should require form_valid implementation"""
        from django import forms

        class TestForm(forms.Form):
            test_field = forms.CharField()

        class TestAction(GeneralActionMixin, FormActionMixin, BaseAction):
            label = 'Test'
            form_class = TestForm

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        factory = RequestFactory()
        request = factory.post('/', {'test_field': 'value'})

        form = action.get_form(request)
        assert form.is_valid()

        with pytest.raises(NotImplementedError):
            action.form_valid(request, form)


class TestConfirmationActionMixin:
    """Test ConfirmationActionMixin functionality"""

    def test_confirmation_view_type(self, admin_site):
        """ConfirmationActionMixin should set view_type"""

        class TestAction(RecordActionMixin, ConfirmationActionMixin, BaseAction):
            label = 'Delete'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.view_type == 'confirmation'

    def test_get_confirmation_message_for_record(self, admin_site, product_factory, db):
        """Should generate confirmation message for single object"""

        class TestAction(RecordActionMixin, ConfirmationActionMixin, BaseAction):
            label = 'Delete'

        product = product_factory(name='Test Product')

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        message = action.get_confirmation_message(obj=product)

        assert 'delete' in message.lower()
        assert 'Test Product' in message

    def test_get_confirmation_message_for_bulk(self, admin_site, product_factory, db):
        """Should generate confirmation message for multiple objects"""

        class TestAction(BulkActionMixin, ConfirmationActionMixin, BaseAction):
            label = 'Delete'

        product_factory.create_batch(5)

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        queryset = Product.objects.all()
        message = action.get_confirmation_message(queryset=queryset)

        assert 'delete' in message.lower()
        assert '5 items' in message

    def test_get_template_name(self, admin_site):
        """Should return confirmation template"""

        class TestAction(RecordActionMixin, ConfirmationActionMixin, BaseAction):
            label = 'Delete'

        admin_site.register(Product, ModelAdmin)
        model_admin = admin_site._registry[Product][0]
        action = TestAction(Product, model_admin, admin_site)

        assert action.get_template_name() == 'djadmin/actions/confirm.html'
