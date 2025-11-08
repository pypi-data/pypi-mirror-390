"""End-to-end integration tests for CRUD action workflows."""

import json
from decimal import Decimal

import pytest
from djadmin_formset.utils import build_create_post_data, build_update_post_data

from djadmin import site
from examples.webshop.models import Product


@pytest.mark.django_db
class TestAddActionIntegration:
    """Test AddAction end-to-end workflow."""

    def test_add_action_displays_form(self, admin_client):
        """AddAction should display a form to create a new product."""
        url = site.reverse('webshop_product_add')
        response = admin_client.get(url)

        assert response.status_code == 200
        assert b'Add' in response.content
        assert b'name' in response.content.lower()

    def test_add_action_creates_product(self, admin_client, category_factory):
        """AddAction should create a new product on valid POST."""
        # Create a category first (required ForeignKey)
        category = category_factory()

        # Get ModelAdmin for building POST data
        model_admin = site.get_model_admins(Product)[0]
        add_action = [a for a in model_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]

        url = site.reverse('webshop_product_add')
        post_data = build_create_post_data(
            add_action,
            name='Test Product',
            slug='test-product',
            sku='TEST-001',
            category=category.pk,
            description='Test product description',
            price='99.99',
            cost='60.00',
            stock_quantity='10',
            status='active',
        )
        response = admin_client.post(
            url,
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # JSON POST returns 200 with success_url instead of 302 redirect
        assert response.status_code == 200
        response_data = response.json()
        # Debug: always print response to see what's happening
        print('\n=== Response Data ===')
        import pprint

        pprint.pprint(response_data)
        print('=== Products in DB ===')
        print(list(Product.objects.values_list('name', flat=True)))
        print('=====================\n')
        assert 'success_url' in response_data
        assert Product.objects.filter(name='Test Product').exists()

        # Check created product
        product = Product.objects.get(name='Test Product')
        assert product.sku == 'TEST-001'
        assert product.price == Decimal('99.99')
        assert product.cost == Decimal('60.00')


@pytest.mark.django_db
class TestEditRecordActionIntegration:
    """Test EditRecordAction end-to-end workflow."""

    def test_edit_action_displays_form_with_data(self, admin_client, product_factory):
        """EditRecordAction should display a form with existing data."""
        product = product_factory(name='Old Name', price=100)

        url = site.reverse('webshop_product_edit', kwargs={'pk': product.pk})
        response = admin_client.get(url)

        assert response.status_code == 200
        assert b'Old Name' in response.content

    def test_edit_action_updates_product(self, admin_client, product_factory):
        """EditRecordAction should update a product on valid POST."""
        product = product_factory(name='Old Name', price=100)

        # Get ModelAdmin for building POST data
        model_admin = site.get_model_admins(Product)[0]
        edit_action = [a for a in model_admin.record_actions if a.__class__.__name__ == 'EditAction'][0]

        url = site.reverse('webshop_product_edit', kwargs={'pk': product.pk})
        post_data = build_update_post_data(
            edit_action,
            instance=product,
            name='New Name',
            price='150.00',
        )
        response = admin_client.post(
            url,
            data=json.dumps(post_data),
            content_type='application/json',
        )

        # JSON POST returns 200 with success_url instead of 302 redirect
        assert response.status_code == 200
        response_data = response.json()
        assert 'success_url' in response_data

        # Check updated product
        product.refresh_from_db()
        assert product.name == 'New Name'
        assert product.price == 150


@pytest.mark.django_db
class TestDeleteRecordActionIntegration:
    """Test DeleteRecordAction end-to-end workflow."""

    def test_delete_action_shows_confirmation(self, admin_client, product_factory):
        """DeleteRecordAction should show confirmation page on GET."""
        product = product_factory(name='To Delete')

        url = site.reverse('webshop_product_delete', kwargs={'pk': product.pk})
        response = admin_client.get(url)

        assert response.status_code == 200
        assert b'To Delete' in response.content
        assert b'sure' in response.content.lower() or b'confirm' in response.content.lower()

    def test_delete_action_removes_product(self, admin_client, product_factory):
        """DeleteRecordAction should delete a product on POST."""
        product = product_factory(name='To Delete')
        product_pk = product.pk

        url = site.reverse('webshop_product_delete', kwargs={'pk': product_pk})
        response = admin_client.post(url)

        # Should redirect to list view
        assert response.status_code == 302
        assert not Product.objects.filter(pk=product_pk).exists()


@pytest.mark.django_db
class TestDeleteBulkActionIntegration:
    """Test DeleteBulkAction end-to-end workflow."""

    def test_bulk_delete_shows_confirmation(self, admin_client, product_factory):
        """DeleteBulkAction should show confirmation page with count."""
        products = product_factory.create_batch(5)
        pks = [p.pk for p in products[:3]]

        url = site.reverse('webshop_product_bulk_delete')
        response = admin_client.get(url, {'_selected_action': pks})

        assert response.status_code == 200
        assert b'3' in response.content

    def test_bulk_delete_removes_products(self, admin_client, product_factory):
        """DeleteBulkAction should delete multiple products on POST."""
        products = product_factory.create_batch(5)
        pks = [p.pk for p in products[:3]]

        initial_count = Product.objects.count()
        assert initial_count == 5

        url = site.reverse('webshop_product_bulk_delete')
        response = admin_client.post(url, {'_selected_action': pks})

        # Should redirect to list view
        assert response.status_code == 302

        # Check deleted
        assert Product.objects.count() == 2
        for pk in pks:
            assert not Product.objects.filter(pk=pk).exists()


@pytest.mark.django_db
class TestFullCRUDWorkflow:
    """Test complete CRUD workflow from start to finish."""

    def test_full_crud_cycle(self, admin_client, category_factory):
        """Test creating, listing, editing, and deleting a product."""
        # Create a category first (required ForeignKey)
        category = category_factory()

        # Get ModelAdmin for building POST data
        model_admin = site.get_model_admins(Product)[0]
        add_action = [a for a in model_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        edit_action = [a for a in model_admin.record_actions if a.__class__.__name__ == 'EditAction'][0]

        # Step 1: Create a product
        add_url = site.reverse('webshop_product_add')
        post_data = build_create_post_data(
            add_action,
            name='Workflow Test Product',
            slug='workflow-test-product',
            sku='WF-001',
            category=category.pk,
            description='Workflow test product description',
            price='49.99',
            cost='30.00',
            stock_quantity='5',
            status='active',
        )
        response = admin_client.post(
            add_url,
            data=json.dumps(post_data),
            content_type='application/json',
        )
        # JSON POST returns 200 with success_url instead of 302 redirect
        assert response.status_code == 200
        response_data = response.json()
        assert 'success_url' in response_data

        # Verify product was created
        product = Product.objects.get(name='Workflow Test Product')
        assert product.sku == 'WF-001'
        assert product.price == Decimal('49.99')

        # Step 2: View product in list
        list_url = site.reverse('webshop_product_list')
        response = admin_client.get(list_url)
        assert response.status_code == 200
        assert b'Workflow Test Product' in response.content

        # Step 3: Edit the product
        edit_url = site.reverse('webshop_product_edit', kwargs={'pk': product.pk})
        post_data = build_update_post_data(
            edit_action,
            instance=product,
            name='Updated Workflow Product',
            price='59.99',
        )
        response = admin_client.post(
            edit_url,
            data=json.dumps(post_data),
            content_type='application/json',
        )
        # JSON POST returns 200 with success_url instead of 302 redirect
        assert response.status_code == 200
        response_data = response.json()
        assert 'success_url' in response_data

        # Verify product was updated
        product.refresh_from_db()
        assert product.name == 'Updated Workflow Product'
        assert product.price == Decimal('59.99')

        # Step 4: Delete the product
        delete_url = site.reverse('webshop_product_delete', kwargs={'pk': product.pk})
        response = admin_client.post(delete_url)
        assert response.status_code == 302

        # Verify product was deleted
        assert not Product.objects.filter(pk=product.pk).exists()
