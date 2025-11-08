"""Tests for management commands"""

import json
from io import StringIO

import pytest
from django.core.management import call_command


@pytest.mark.django_db
class TestDjAdminInspect:
    """Test djadmin_inspect management command"""

    def test_inspect_all_admins(self):
        """Test inspecting all registered admins"""
        out = StringIO()
        call_command('djadmin_inspect', stdout=out)
        output = out.getvalue()

        # Should contain ProductAdmin
        assert 'ProductAdmin' in output
        assert 'webshop.Product' in output

    def test_inspect_specific_model(self):
        """Test inspecting specific model"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', stdout=out)
        output = out.getvalue()

        assert 'ProductAdmin' in output
        assert 'ListAction' in output
        assert 'AddAction' in output

    def test_inspect_json_format(self):
        """Test JSON output format"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', '--format', 'json', stdout=out)
        output = out.getvalue()

        # Should be valid JSON
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'admin_class' in data[0]
        assert data[0]['admin_class'] == 'ProductAdmin'

    def test_inspect_shows_base_class_and_mixins(self):
        """Test that base class and mixins are shown for views"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', stdout=out)
        output = out.getvalue()

        # Should show view composition
        assert 'Base Class:' in output
        assert 'Mixins:' in output
        assert 'DjAdminViewMixin' in output

    def test_inspect_shows_features(self):
        """Test that requested features are shown"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', stdout=out)
        output = out.getvalue()

        # ProductAdmin has search_fields, so should show search feature
        assert 'REQUESTED FEATURES' in output
        assert 'search' in output

    def test_inspect_filter_by_action_type_general(self):
        """Test filtering by general action type"""
        out = StringIO()
        call_command(
            'djadmin_inspect',
            '--model',
            'webshop.Product',
            '--actions',
            'general',
            stdout=out,
        )
        output = out.getvalue()

        assert 'General Actions' in output
        assert 'ListAction' in output
        # Should NOT show other action types
        assert 'Bulk Actions' not in output
        assert 'Record Actions' not in output

    def test_inspect_filter_by_action_type_bulk(self):
        """Test filtering by bulk action type"""
        out = StringIO()
        call_command(
            'djadmin_inspect',
            '--model',
            'webshop.Product',
            '--actions',
            'bulk',
            stdout=out,
        )
        output = out.getvalue()

        assert 'Bulk Actions' in output
        assert 'DeleteBulkAction' in output
        # Should NOT show other action types
        assert 'General Actions' not in output
        assert 'Record Actions' not in output

    def test_inspect_filter_by_action_type_record(self):
        """Test filtering by record action type"""
        out = StringIO()
        call_command(
            'djadmin_inspect',
            '--model',
            'webshop.Product',
            '--actions',
            'record',
            stdout=out,
        )
        output = out.getvalue()

        assert 'Record Actions' in output
        assert 'EditAction' in output
        # Should NOT show other action types
        assert 'General Actions' not in output
        assert 'Bulk Actions' not in output

    def test_inspect_shows_forms(self):
        """Test that forms are shown for form actions"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', '--actions', 'record', stdout=out)
        output = out.getvalue()

        # EditRecordAction should show form info
        assert 'Form: ProductForm' in output

    def test_inspect_shows_templates(self):
        """Test that template resolution order is shown"""
        out = StringIO()
        call_command('djadmin_inspect', '--model', 'webshop.Product', stdout=out)
        output = out.getvalue()

        assert 'TEMPLATES (resolution order)' in output
        assert 'djadmin/webshop/product_list.html' in output

    def test_inspect_invalid_model(self):
        """Test inspecting non-existent model"""
        out = StringIO()
        err = StringIO()
        call_command('djadmin_inspect', '--model', 'invalid.Invalid', stdout=out, stderr=err)
        output = out.getvalue() + err.getvalue()

        # Should show warning about not finding model
        assert 'No admins found' in output or 'Failed to find model' in output

    def test_inspect_shows_example_for_filtered_action_type(self):
        """Test that action example matches the filter"""
        out = StringIO()
        call_command(
            'djadmin_inspect',
            '--model',
            'webshop.Product',
            '--actions',
            'bulk',
            stdout=out,
        )
        output = out.getvalue()

        # Should show bulk action view composition, not general/record
        assert 'VIEW COMPOSITION - DeleteBulkAction' in output
        assert 'VIEW COMPOSITION - ListAction' not in output
        assert 'VIEW COMPOSITION - EditAction' not in output
