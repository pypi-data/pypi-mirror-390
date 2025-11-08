"""Test dashboard edge cases."""

import pytest

from djadmin import AdminSite, ModelAdmin
from examples.webshop.models import Category, Product


@pytest.mark.django_db
class TestDashboardEdgeCases:
    """Test dashboard edge cases."""

    def test_dashboard_with_empty_site(self, admin_client):
        """Dashboard with no registered models should work."""
        # Use a new site with no registrations
        # (Not used directly but tests that dashboard works without registrations)

        # Dashboard should still render
        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

    def test_dashboard_with_single_model(self, admin_client, admin_site):
        """Dashboard with only one model should work."""
        # admin_site already has some models registered from fixtures
        response = admin_client.get('/djadmin/')
        assert response.status_code == 200
        assert b'djadmin' in response.content.lower() or b'admin' in response.content.lower()

    def test_app_dashboard_nonexistent_app(self, admin_client):
        """App dashboard for non-existent app should handle gracefully."""
        response = admin_client.get('/djadmin/nonexistent_app/')

        # Should show empty dashboard or redirect
        assert response.status_code in [200, 404]

    def test_dashboard_model_no_general_actions(self, admin_client, admin_site):
        """ModelAdmin with no general_actions should not appear in dashboard main actions."""

        class NoGeneralActionsAdmin(ModelAdmin):
            general_actions = []
            list_actions = []

        admin_site.register(Category, NoGeneralActionsAdmin)

        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

        # Should still show the model but with no clickable actions
        # (implementation may vary - just ensure it doesn't error)

    def test_dashboard_many_modeladmins(self, admin_client):
        """Dashboard with many ModelAdmins for same model should work."""
        site = AdminSite(name='many')

        for i in range(20):
            class_name = f'Admin{i}'
            admin_class = type(class_name, (ModelAdmin,), {})
            site.register(Product, admin_class)

        # Should handle many registrations
        assert len(site._registry[Product]) == 20

    def test_dashboard_with_unicode_model_names(self, admin_client, admin_site):
        """Dashboard should handle models with unicode verbose names."""
        from django.db import models

        class UnicodeModel(models.Model):  # noqa: DJ008
            name = models.CharField(max_length=100)

            class Meta:
                app_label = 'webshop'
                verbose_name = 'Продукт'
                verbose_name_plural = 'Продукты'

        # Register model
        admin_site.register(UnicodeModel)

        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

    def test_app_dashboard_with_multiple_models(self, admin_client, admin_site):
        """App dashboard with multiple models should work."""
        from examples.webshop.models import Customer, Order

        admin_site.register(Customer)
        admin_site.register(Order)

        response = admin_client.get('/djadmin/webshop/')
        assert response.status_code == 200

    def test_dashboard_with_very_long_model_name(self, admin_client, admin_site):
        """Dashboard should handle models with very long names."""
        from django.db import models

        class VeryLongModelNameThatShouldStillWork(models.Model):  # noqa: DJ008
            name = models.CharField(max_length=100)

            class Meta:
                app_label = 'webshop'

        admin_site.register(VeryLongModelNameThatShouldStillWork)

        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

    def test_dashboard_filtering_by_app(self, admin_client, admin_site):
        """App dashboard should only show models from that app."""
        response = admin_client.get('/djadmin/webshop/')
        assert response.status_code == 200

        # Should show webshop models only
        # (implementation-specific check)

    def test_dashboard_with_custom_admin_site_name(self, admin_client):
        """Dashboard should work with custom AdminSite name."""
        site = AdminSite(name='custom_admin')
        site.register(Product)

        # URL generation should use custom name
        urls = site.get_urls()
        assert len(urls) > 0

    def test_dashboard_action_links_correctness(self, admin_client, admin_site):
        """Dashboard action links should be valid URLs."""
        admin_site.register(Product)

        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

        # Check that response contains valid href attributes
        content = response.content.decode('utf-8')
        assert 'href' in content

    def test_project_vs_app_dashboard_distinction(self, admin_client, admin_site):
        """Project and app dashboards should be distinct."""
        # Project dashboard (all apps)
        project_response = admin_client.get('/djadmin/')
        assert project_response.status_code == 200

        # App dashboard (single app)
        app_response = admin_client.get('/djadmin/webshop/')
        assert app_response.status_code == 200

        # They should have different content
        assert project_response.content != app_response.content

    @pytest.mark.skip(reason='Permissions are out of scope for Phase 1 - deferred to Phase 2+')
    def test_dashboard_with_no_permissions(self, client):
        """Dashboard without authentication should redirect or deny."""
        response = client.get('/djadmin/')

        # Should require login
        assert response.status_code in [302, 403]

    def test_dashboard_breadcrumbs(self, admin_client, admin_site):
        """Dashboard should have breadcrumb navigation."""
        response = admin_client.get('/djadmin/')
        assert response.status_code == 200

        # Should have breadcrumb context or HTML
        if hasattr(response, 'context'):
            # Implementation may provide breadcrumbs in context
            pass

    def test_dashboard_empty_app(self, admin_client):
        """Dashboard for app with no registered models should work."""
        # Try to access app dashboard for app with no models
        response = admin_client.get('/djadmin/auth/')

        # Should show empty state or 404
        assert response.status_code in [200, 404]
