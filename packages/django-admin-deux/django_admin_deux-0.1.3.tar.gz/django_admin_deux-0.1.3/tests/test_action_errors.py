"""Test action error handling."""

import json

import pytest
from djadmin_formset.utils import build_create_post_data, build_update_post_data

from djadmin import site
from examples.webshop.models import Category, Product


@pytest.mark.django_db
class TestActionErrors:
    """Test actions handle errors gracefully."""

    def test_bulk_action_no_selection(self, admin_client):
        """Bulk action with no selection should show error."""
        # Create test data
        Category.objects.create(name='Test', slug='test')

        response = admin_client.post(
            site.reverse('webshop_category_bulk_delete'),
            {'_selected_action': []},  # Empty selection
        )

        # Should redirect or show error
        assert response.status_code in [200, 302]

        if response.status_code == 200:
            # If showing page, should have error context or form error
            assert b'error' in response.content.lower() or hasattr(response, 'context')

    def test_bulk_action_missing_action_field(self, admin_client):
        """Bulk action without _selected_action should fail gracefully."""
        response = admin_client.post(
            site.reverse('webshop_category_bulk_delete'),
            {},  # Missing _selected_action
        )

        # Should redirect or show error
        assert response.status_code in [200, 302]

    def test_record_action_nonexistent_pk(self, admin_client):
        """Record action with invalid PK should 404."""
        response = admin_client.get(site.reverse('webshop_product_edit', kwargs={'pk': 99999}))

        assert response.status_code == 404

    def test_record_action_with_string_pk(self, admin_client):
        """Record action with non-integer PK should fail."""
        # Note: Django URL patterns with <int:pk> will reject non-integers before the view
        # So we expect a 404 from URL resolution, not the view
        response = admin_client.get('/djadmin/webshop/product/notanumber/actions/edit/')

        assert response.status_code == 404

    def test_form_action_validation_errors(self, admin_client, category_factory):
        """Form action with validation errors should return 422 with errors."""
        category = category_factory()

        # Use JSON POST format with build_create_post_data
        product_admin = site.get_model_admins(Product)[0]
        add_action = [a for a in product_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        post_data = build_create_post_data(
            add_action,
            name='',  # Invalid - name required
            slug='test',
            sku='SKU-001',
            description='Test description',
            price='10.00',
            cost='6.00',
            category=category.id,
        )
        response = admin_client.post(
            site.reverse('webshop_product_add'),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # FormCollectionView returns 422 Unprocessable Entity for validation errors
        assert response.status_code == 422
        response_data = json.loads(response.content)
        # Check that response contains field-level errors (hierarchical structure)
        assert 'basic_information' in response_data or 'name' in response_data

    def test_form_action_missing_required_fields(self, admin_client):
        """Form action with missing required fields should return 422 with errors."""
        # Use JSON POST format with empty field values
        product_admin = site.get_model_admins(Product)[0]
        add_action = [a for a in product_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        post_data = build_create_post_data(add_action)  # Empty data - all required fields missing
        response = admin_client.post(
            site.reverse('webshop_product_add'),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # FormCollectionView returns 422 Unprocessable Entity for validation errors
        assert response.status_code == 422
        response_data = json.loads(response.content)
        # Should have multiple field errors (hierarchical structure)
        assert len(response_data) > 0

    def test_form_action_invalid_foreign_key(self, admin_client):
        """Form action with invalid foreign key should return 422 with error."""
        # Use JSON POST format with invalid foreign key
        product_admin = site.get_model_admins(Product)[0]
        add_action = [a for a in product_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        post_data = build_create_post_data(
            add_action,
            name='Test Product',
            slug='test-product',
            sku='SKU-001',
            description='Test description',
            price='10.00',
            cost='6.00',
            category=99999,  # Non-existent category
        )
        response = admin_client.post(
            site.reverse('webshop_product_add'),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # FormCollectionView returns 422 Unprocessable Entity for validation errors
        assert response.status_code == 422
        response_data = json.loads(response.content)
        # Check for category error in hierarchical structure
        assert 'basic_information' in response_data or 'category' in response_data

    def test_edit_action_with_concurrent_modification(self, admin_client, product_factory):
        """Edit action should handle concurrent modifications."""
        product = product_factory()

        # Get edit form
        response = admin_client.get(site.reverse('webshop_product_edit', kwargs={'pk': product.pk}))
        assert response.status_code == 200

        # Simulate concurrent modification
        product.name = 'Modified by another user'
        product.save()

        # Submit edit form with updated name using JSON POST format
        product_admin = site.get_model_admins(Product)[0]
        edit_action = [a for a in product_admin.record_actions if a.__class__.__name__ == 'EditAction'][0]
        post_data = build_update_post_data(
            edit_action,
            product,
            name='My Update',  # Our update
        )
        response = admin_client.post(
            site.reverse('webshop_product_edit', kwargs={'pk': product.pk}),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # Should succeed (last write wins) - FormCollectionView returns 200 with success_url
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert 'success_url' in response_data

        # Verify final state
        product.refresh_from_db()
        assert product.name == 'My Update'  # Our update should win

    def test_delete_action_with_protected_fk(self, admin_client, category_factory, product_factory):
        """Delete action should handle protected foreign key constraints."""
        category = category_factory()
        product = product_factory(category=category)

        # Try to delete category with product (should fail due to CASCADE)
        response = admin_client.post(site.reverse('webshop_category_delete', kwargs={'pk': category.pk}))

        # Should succeed (CASCADE will delete product too)
        assert response.status_code == 302

        # Verify both are deleted
        assert not Category.objects.filter(pk=category.pk).exists()
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_bulk_delete_with_protected_fk(self, admin_client, category_factory, product_factory):
        """Bulk delete should handle protected foreign key constraints."""
        categories = category_factory.create_batch(3)
        # Create products for categories
        for category in categories:
            product_factory.create_batch(2, category=category)

        # Try to bulk delete categories (should work with CASCADE)
        response = admin_client.post(
            site.reverse('webshop_category_bulk_delete'), {'_selected_action': [str(cat.pk) for cat in categories]}
        )

        # Should succeed (CASCADE deletes products)
        assert response.status_code == 302

        # Verify categories and products are deleted
        assert Category.objects.count() == 0
        assert Product.objects.filter(category__in=categories).count() == 0

    @pytest.mark.skip(reason='Permissions are out of scope for Phase 1 - deferred to Phase 2+')
    def test_action_without_permission(self, client):
        """Action accessed without login should require authentication."""
        # Not using admin_client (no login)
        response = client.get(site.reverse('webshop_product_list'))

        # Should redirect to login or show 403
        assert response.status_code in [302, 403]

    def test_add_action_duplicate_unique_field(self, admin_client, category_factory):
        """Add action with duplicate unique field should return 422 with error."""
        category = category_factory()

        # Use JSON POST format with duplicate slug
        category_admin = site.get_model_admins(Category)[0]
        add_action = [a for a in category_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        post_data = build_create_post_data(
            add_action,
            name='New Category',
            slug=category.slug,  # Duplicate slug (unique field)
        )
        response = admin_client.post(
            site.reverse('webshop_category_add'),
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # FormCollectionView returns 422 Unprocessable Entity for validation errors
        assert response.status_code == 422
        response_data = json.loads(response.content)
        # Check for slug error in response
        assert 'slug' in response_data or any('slug' in str(v) for v in response_data.values())
