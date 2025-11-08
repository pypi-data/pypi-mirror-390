"""
Tests for URL routing and reverse lookups.

Phase 1D focuses on:
- Project dashboard (index)
- App dashboards (per app)
- ListView URLs (per model)

Note: Create and Detail views will be added via actions in Milestone 3.
"""

import pytest
from django.urls import NoReverseMatch, reverse

from djadmin import AdminSite, ModelAdmin
from examples.webshop.models import Category, Customer, Order, Product


@pytest.fixture
def configured_site():
    """AdminSite with multiple registered models across different apps"""
    site = AdminSite(name='test_admin')

    # Phase 2.5: Disable permissions for URL routing tests (Type A - structure testing)
    class ProductAdmin(ModelAdmin):
        list_display = ['name', 'sku', 'price']
        permission_class = None

    class CategoryAdmin(ModelAdmin):
        list_display = ['name', 'parent']
        permission_class = None

    class CustomerAdmin(ModelAdmin):
        list_display = ['email', 'first_name', 'last_name']
        permission_class = None

    site.register(Product, ProductAdmin)
    site.register(Category, CategoryAdmin)
    site.register(Customer, CustomerAdmin)

    return site


def test_admin_site_urls_property(configured_site):
    """Test that urls property returns correct tuple for include()"""
    urls = configured_site.urls

    # Should return (urlpatterns, app_name)
    assert isinstance(urls, tuple)
    assert len(urls) == 2

    urlpatterns, app_name = urls
    assert isinstance(urlpatterns, list)
    assert app_name == 'test_admin'


def test_admin_site_get_urls_structure(configured_site):
    """Test that get_urls generates correct URL patterns"""
    urlpatterns = configured_site.get_urls()

    # Should have:
    # - 1 project dashboard (index)
    # - 1 app dashboard (webshop - all models are from webshop app)
    # - 3 models × 2 general actions (ListView, Add) = 6
    # - 3 models × 3 record actions (View, Edit, Delete) = 9
    # - 3 models × 1 bulk action (Delete Bulk) = 3
    # Total: 1 + 1 + 6 + 9 + 3 = 20 URLs
    assert len(urlpatterns) == 20


def test_project_dashboard_url_pattern(configured_site):
    """Test project dashboard URL pattern"""
    urlpatterns = configured_site.get_urls()

    # First pattern should be project dashboard
    pattern = urlpatterns[0]
    assert pattern.name == 'index'
    assert str(pattern.pattern) == ''


def test_app_dashboard_url_pattern(configured_site):
    """Test app dashboard URL pattern"""
    urlpatterns = configured_site.get_urls()

    # Should have one app dashboard for 'webshop'
    app_patterns = [p for p in urlpatterns if 'app_index' in p.name]
    assert len(app_patterns) == 1

    pattern = app_patterns[0]
    assert pattern.name == 'webshop_app_index'
    assert str(pattern.pattern) == 'webshop/'


def test_model_list_url_patterns(configured_site):
    """Test model list URL patterns"""
    urlpatterns = configured_site.get_urls()

    # Find list URL patterns (each model has 1 ListView URL)
    list_patterns = [p for p in urlpatterns if p.name.endswith('_list')]
    assert len(list_patterns) == 3  # 3 models × 1 URL each

    # Check Product list URL
    product_pattern = next(p for p in list_patterns if p.name == 'webshop_product_list')
    assert str(product_pattern.pattern) == 'webshop/product/'

    # Check Category list URL
    category_pattern = next(p for p in list_patterns if p.name == 'webshop_category_list')
    assert str(category_pattern.pattern) == 'webshop/category/'

    # Check Customer list URL
    customer_pattern = next(p for p in list_patterns if p.name == 'webshop_customer_list')
    assert str(customer_pattern.pattern) == 'webshop/customer/'


def test_url_patterns_for_all_registered_models(configured_site):
    """Test that URL patterns are generated for all registered models"""
    urlpatterns = configured_site.get_urls()

    # Expected pattern names:
    # - Each model gets 1 ListView URL
    # - Each model gets 1 Add action URL
    # - Each model gets 3 record action URLs (View, Edit, Delete)
    # - Each model gets 1 bulk action URL (DeleteBulk)
    expected_names = [
        'index',
        'webshop_app_index',
        # Product URLs (note: semantic URL names after Phase 5A)
        'webshop_product_list',  # ListView
        'webshop_product_add',  # Add action
        'webshop_product_view',  # View action (read-only)
        'webshop_product_edit',  # Edit action (was editrecord)
        'webshop_product_delete',  # Delete action (was deleterecord)
        'webshop_product_bulk_delete',  # Bulk delete action (was deletebulk)
        # Category URLs
        'webshop_category_list',  # ListView
        'webshop_category_add',  # Add action
        'webshop_category_view',  # View action (read-only)
        'webshop_category_edit',  # Edit action (was editrecord)
        'webshop_category_delete',  # Delete action (was deleterecord)
        'webshop_category_bulk_delete',  # Bulk delete action (was deletebulk)
        # Customer URLs
        'webshop_customer_list',  # ListView
        'webshop_customer_add',  # Add action
        'webshop_customer_view',  # View action (read-only)
        'webshop_customer_edit',  # Edit action (was editrecord)
        'webshop_customer_delete',  # Delete action (was deleterecord)
        'webshop_customer_bulk_delete',  # Bulk delete action (was deletebulk)
    ]

    pattern_names = [p.name for p in urlpatterns]
    assert set(pattern_names) == set(expected_names)


def test_multiple_apps_generate_multiple_app_dashboards():
    """Test that models from different apps generate separate app dashboards"""
    site = AdminSite(name='multi_app')

    # Register models from webshop app
    site.register(Product)
    site.register(Category)

    urlpatterns = site.get_urls()

    # Should have: 1 project dashboard + 1 app dashboard +
    # (2 models × 2 general actions: ListView + Add) +
    # (2 models × 3 record actions: View, Edit, Delete) + (2 models × 1 bulk action)
    # Total: 1 + 1 + 4 + 6 + 2 = 14
    assert len(urlpatterns) == 14

    # Check app dashboard exists
    app_patterns = [p for p in urlpatterns if 'app_index' in p.name]
    assert len(app_patterns) == 1
    assert app_patterns[0].name == 'webshop_app_index'


def test_url_pattern_naming_convention(configured_site):
    """Test that URL pattern names follow the convention"""
    urlpatterns = configured_site.get_urls()

    for pattern in urlpatterns:
        if pattern.name == 'index':
            continue

        # App dashboards should be: <app>_app_index
        if pattern.name.endswith('_app_index'):
            parts = pattern.name.split('_')
            assert len(parts) == 3
            assert parts[-2] == 'app'
            assert parts[-1] == 'index'
            continue

        # Model list patterns should be: <app>_<model>_list
        if pattern.name.endswith('_list'):
            parts = pattern.name.split('_')
            assert len(parts) >= 3
            assert parts[-1] == 'list'


class TestURLReverseLookups:
    """Test reverse URL lookups with namespace"""

    @pytest.fixture(autouse=True)
    def setup_urls(self, configured_site, settings):
        """Set up URLconf for reverse lookup tests"""
        from django.urls import include, path

        # Use include() with the 3-tuple returned by site.urls
        # This automatically sets up the namespace
        urlpatterns = [
            path('djadmin/', include(configured_site.urls)),
        ]

        # Temporarily override ROOT_URLCONF
        settings.ROOT_URLCONF = type('URLConf', (), {'urlpatterns': urlpatterns})

    def test_reverse_project_dashboard(self):
        """Test reverse lookup for project dashboard"""
        url = reverse('test_admin:index')
        assert url == '/djadmin/'

    def test_reverse_app_dashboard(self):
        """Test reverse lookup for app dashboard"""
        url = reverse('test_admin:webshop_app_index')
        assert url == '/djadmin/webshop/'

    def test_reverse_model_list(self):
        """Test reverse lookup for model list view"""
        url = reverse('test_admin:webshop_product_list')
        assert url == '/djadmin/webshop/product/'

    def test_reverse_all_model_lists(self):
        """Test reverse lookup for all registered model list views"""
        models = [
            ('webshop', 'product'),
            ('webshop', 'category'),
            ('webshop', 'customer'),
        ]

        for app_label, model_name in models:
            url = reverse(f'test_admin:{app_label}_{model_name}_list')
            assert url == f'/djadmin/{app_label}/{model_name}/'

    def test_reverse_nonexistent_model_raises(self):
        """Test that reversing nonexistent model URL raises NoReverseMatch"""
        with pytest.raises(NoReverseMatch):
            reverse('test_admin:webshop_nonexistent_list')

    def test_reverse_nonexistent_app_raises(self):
        """Test that reversing nonexistent app dashboard raises NoReverseMatch"""
        with pytest.raises(NoReverseMatch):
            reverse('test_admin:nonexistent_app_index')


@pytest.mark.django_db
class TestViewResponses:
    """Test view responses"""

    @pytest.fixture(autouse=True)
    def setup_urls(self, configured_site, settings):
        """Set up URLconf for view tests"""
        from django.urls import include, path

        urlpatterns = [
            path('djadmin/', include(configured_site.urls)),
        ]

        settings.ROOT_URLCONF = type('URLConf', (), {'urlpatterns': urlpatterns})

    def test_project_dashboard_view(self, authenticated_client):
        """Test project dashboard view"""
        response = authenticated_client.get('/djadmin/')
        assert response.status_code == 200
        # Check for Dashboard heading
        assert b'Dashboard' in response.content

    def test_app_dashboard_view(self, authenticated_client):
        """Test app dashboard view"""
        response = authenticated_client.get('/djadmin/webshop/')
        assert response.status_code == 200
        # Check for app name (capitalized) in template
        assert b'Webshop' in response.content

    def test_model_list_view(self, client):
        """Test model list view"""
        response = client.get('/djadmin/webshop/product/')
        assert response.status_code == 200
        # Check for model list content from template
        assert b'Products' in response.content  # verbose_name_plural
        assert b'Webshop - Products' in response.content  # Page header format

    def test_all_model_list_views(self, client):
        """Test all model list views"""
        models = [
            ('webshop', 'Product', 'Products'),
            ('webshop', 'Category', 'Categories'),
            ('webshop', 'Customer', 'Customers'),
        ]

        for app_label, model_name, verbose_plural in models:
            response = client.get(f'/djadmin/{app_label}/{model_name.lower()}/')
            assert response.status_code == 200
            # Check for model verbose name in template
            assert verbose_plural.encode() in response.content
            # Check for new page header format: "App - Model"
            assert f'{app_label.title()} - {verbose_plural}'.encode() in response.content


def test_multiple_admin_sites_independent():
    """Test that multiple AdminSite instances have independent URLs"""
    site1 = AdminSite(name='site1')
    site2 = AdminSite(name='site2')

    site1.register(Product)
    site2.register(Category)

    urls1 = site1.get_urls()
    urls2 = site2.get_urls()

    # Site 1 should only have Product URLs
    pattern_names1 = [p.name for p in urls1]
    assert 'webshop_product_list' in pattern_names1
    assert 'webshop_category_list' not in pattern_names1

    # Site 2 should only have Category URLs
    pattern_names2 = [p.name for p in urls2]
    assert 'webshop_category_list' in pattern_names2
    assert 'webshop_product_list' not in pattern_names2


def test_url_generation_with_no_registered_models():
    """Test URL generation when no models are registered"""
    site = AdminSite(name='empty')
    urlpatterns = site.get_urls()

    # Should only have project dashboard
    assert len(urlpatterns) == 1
    assert urlpatterns[0].name == 'index'


def test_url_namespace_with_include(configured_site):
    """Test URL namespace when used with include()"""
    # The site.urls property returns a 2-tuple (urlpatterns, app_name)
    # When used with include(), Django automatically sets up the namespace
    # Example usage (not executed):
    # from django.urls import include, path
    # urlpatterns = [path('admin/', include(configured_site.urls))]

    # Verify the structure
    urls_tuple = configured_site.urls
    assert len(urls_tuple) == 2
    assert urls_tuple[1] == 'test_admin'  # app_name


def test_url_without_namespace(configured_site):
    """Test that site.urls works with include()"""
    # The site.urls property returns a 2-tuple that must be passed to include()
    # Django's path() doesn't accept the tuple directly
    # Example usage (not executed):
    # from django.urls import include, path
    # urlpatterns = [path('admin/', include(configured_site.urls))]

    # Site.urls returns tuple that works with include()
    assert isinstance(configured_site.urls, tuple)
    assert len(configured_site.urls) == 2


def test_same_model_registered_multiple_times():
    """Test URL generation when same model is registered multiple times"""
    site = AdminSite(name='multi')

    # Phase 2.5: Disable permissions for URL routing tests (Type A - structure testing)
    class ProductAdmin1(ModelAdmin):
        list_display = ['name']
        permission_class = None

    class ProductAdmin2(ModelAdmin):
        list_display = ['name', 'sku']
        permission_class = None

    site.register(Product, ProductAdmin1)
    site.register(Product, ProductAdmin2)

    urlpatterns = site.get_urls()

    # Should have: 1 project + 1 app +
    # (2 admins × 2 general actions: ListView + Add) +
    # (2 admins × 3 record actions: View, Edit, Delete) + (2 admins × 1 bulk action)
    # Total: 1 + 1 + 4 + 6 + 2 = 14 URLs
    # NOTE: Multiple ModelAdmins per model currently creates duplicate URLs (same URL name)
    # This will be addressed in a future phase
    assert len(urlpatterns) == 14

    # Both admins currently use the same URL name (last one wins)
    list_patterns = [p for p in urlpatterns if p.name == 'webshop_product_list']
    assert len(list_patterns) >= 1


def test_app_dashboard_created_per_app():
    """Test that one app dashboard is created per unique app label"""
    site = AdminSite(name='test')

    # Register multiple models from same app
    site.register(Product)
    site.register(Category)
    site.register(Customer)
    site.register(Order)

    urlpatterns = site.get_urls()

    # Should have: 1 project + 1 app +
    # (4 models × 2 general actions: ListView + Add) +
    # (4 models × 3 record actions: View, Edit, Delete) + (4 models × 1 bulk action)
    # Total: 1 + 1 + 8 + 12 + 4 = 26 URLs
    assert len(urlpatterns) == 26

    # Should have only one app dashboard for 'webshop'
    app_dashboards = [p for p in urlpatterns if 'app_index' in p.name]
    assert len(app_dashboards) == 1
    assert app_dashboards[0].name == 'webshop_app_index'


def test_url_with_custom_site_name():
    """Test URLs with custom AdminSite name"""
    site = AdminSite(name='custom_admin')
    site.register(Product)

    urls_tuple = site.urls
    assert len(urls_tuple) == 2
    assert urls_tuple[1] == 'custom_admin'  # app_name
