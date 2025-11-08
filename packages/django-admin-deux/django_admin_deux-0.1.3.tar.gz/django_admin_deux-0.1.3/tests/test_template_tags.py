"""Tests for djadmin template tags."""

from django.http import HttpRequest, QueryDict
from django.template import Context, Template
from django.test import TestCase


class TestQueryParamsAsHiddenInputs(TestCase):
    """Test query_params_as_hidden_inputs template tag."""

    def test_preserves_all_parameters_except_excluded(self):
        """Test that all params except excluded ones are converted to hidden inputs."""
        # Create request with multiple parameters
        request = HttpRequest()
        request.GET = QueryDict('search=test&category=1&ordering=name&page=2')

        # Render template excluding search and page
        template = Template('{% load djadmin_tags %}{% query_params_as_hidden_inputs "search" "page" %}')
        context = Context({'request': request})
        output = template.render(context)

        # Should have hidden inputs for category and ordering
        self.assertIn('<input type="hidden" name="category" value="1">', output)
        self.assertIn('<input type="hidden" name="ordering" value="name">', output)

        # Should NOT have hidden inputs for search and page
        self.assertNotIn('name="search"', output)
        self.assertNotIn('name="page"', output)

    def test_handles_multiple_values_for_same_param(self):
        """Test that multiple values for the same parameter are handled."""
        # Create request with list parameter
        request = HttpRequest()
        request.GET = QueryDict('tags=python&tags=django&search=test')

        # Render template excluding search
        template = Template('{% load djadmin_tags %}{% query_params_as_hidden_inputs "search" %}')
        context = Context({'request': request})
        output = template.render(context)

        # Should have two hidden inputs for tags
        self.assertIn('<input type="hidden" name="tags" value="python">', output)
        self.assertIn('<input type="hidden" name="tags" value="django">', output)

    def test_handles_dict_keys_from_form_fields(self):
        """Test that form.fields dict_keys can be passed as exclude."""

        class MockForm:
            def __init__(self):
                self.fields = {'name': None, 'price': None, 'category': None}

        request = HttpRequest()
        request.GET = QueryDict('name=test&price=100&search=query&ordering=name')

        # Render template excluding form fields
        template = Template('{% load djadmin_tags %}{% query_params_as_hidden_inputs filterset.form.fields %}')
        context = Context({'request': request, 'filterset': type('obj', (object,), {'form': MockForm()})})
        output = template.render(context)

        # Should have hidden inputs for search and ordering
        self.assertIn('<input type="hidden" name="search" value="query">', output)
        self.assertIn('<input type="hidden" name="ordering" value="name">', output)

        # Should NOT have hidden inputs for form fields
        self.assertNotIn('name="name"', output)
        self.assertNotIn('name="price"', output)
        self.assertNotIn('name="category"', output)

    def test_returns_empty_string_when_no_request(self):
        """Test that empty string is returned when request is not in context."""
        template = Template('{% load djadmin_tags %}{% query_params_as_hidden_inputs "search" %}')
        context = Context({})
        output = template.render(context)

        self.assertEqual(output.strip(), '')

    def test_escapes_html_in_values(self):
        """Test that HTML in parameter values is properly escaped."""
        request = HttpRequest()
        request.GET = QueryDict('search=%3Cscript%3Ealert%28%22xss%22%29%3C%2Fscript%3E')

        template = Template('{% load djadmin_tags %}{% query_params_as_hidden_inputs "page" %}')
        context = Context({'request': request})
        output = template.render(context)

        # Value should be escaped
        self.assertIn('&lt;script&gt;', output)
        self.assertNotIn('<script>', output)
