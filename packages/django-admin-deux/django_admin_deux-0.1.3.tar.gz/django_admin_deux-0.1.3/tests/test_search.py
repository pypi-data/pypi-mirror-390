"""Tests for search functionality."""

from django.test import TestCase, override_settings

from djadmin import ModelAdmin, site
from examples.webshop.factories import CategoryFactory
from examples.webshop.models import Category


# Dynamic URLconf that regenerates URLs on each request
# This allows tests to register/unregister admins and see fresh URLs
class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestSearchMixin(TestCase):
    """Test the SearchMixin functionality."""

    def setUp(self):
        """Set up test data and clear site registry before each test."""
        # Clear site registry before each test to ensure clean state
        if site.is_registered(Category):
            site.unregister(Category)

        # Create test categories (including parent)
        # Explicitly set descriptions to avoid random Faker text containing search terms
        self.parent = CategoryFactory(
            name='Electronics', slug='electronics', description='Parent category for electronics', is_active=True
        )
        self.categories = [
            CategoryFactory(
                name='Laptop Computers',
                slug='laptop-computers',
                description='High performance devices',
                parent=self.parent,
                is_active=True,
            ),
            CategoryFactory(
                name='Desktop Computers',
                slug='desktop-computers',
                description='Desktop computing devices',
                parent=self.parent,
                is_active=True,
            ),
            CategoryFactory(
                name='Computer Accessories',
                slug='computer-accessories',
                description='Accessories for computers',
                parent=self.parent,
                is_active=True,
            ),
            CategoryFactory(
                name='Office Supplies',
                slug='office-supplies',
                description='Supplies for the office',
                parent=None,
                is_active=True,
            ),
        ]

    def tearDown(self):
        """Clean up site registry after each test."""
        # Unregister Category to ensure no test pollution
        if site.is_registered(Category):
            site.unregister(Category)

        # Force Django to reload URLs on next request
        from django.urls import clear_url_caches

        clear_url_caches()
        # Also clear the test client's resolver cache
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def test_search_single_word(self):
        """Test searching with a single word."""

        # Register CategoryAdmin with search_fields
        # Phase 2.5: Disable permissions for search functionality tests (Type A)
        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['name', 'description', 'slug']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search for 'Computer'
        url = site.reverse('webshop_category_list') + '?search=Computer'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should find all three categories with "Computer" in the name
        self.assertIn(self.categories[0], response.context['object_list'])  # Laptop Computers
        self.assertIn(self.categories[1], response.context['object_list'])  # Desktop Computers
        self.assertIn(self.categories[2], response.context['object_list'])  # Computer Accessories
        self.assertNotIn(self.categories[3], response.context['object_list'])  # Office Supplies
        self.assertNotIn(self.parent, response.context['object_list'])  # Electronics

    def test_search_multiple_words(self):
        """Test searching with multiple words (AND behavior)."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['name', 'description', 'slug']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search for 'Laptop High' - both words must match
        url = site.reverse('webshop_category_list') + '?search=Laptop+High'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Only Laptop Computers should match (has both 'Laptop' in name and 'High' in description)
        self.assertIn(self.categories[0], response.context['object_list'])
        self.assertNotIn(self.categories[1], response.context['object_list'])
        self.assertEqual(len(response.context['object_list']), 1)

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['name', 'slug']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search with different cases
        for query in ['laptop', 'LAPTOP', 'Laptop', 'lApToP']:
            url = site.reverse('webshop_category_list') + f'?search={query}'
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertIn(self.categories[0], response.context['object_list'])

    def test_search_related_field(self):
        """Test searching on related model fields."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['name', 'parent__name']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search for parent category name
        url = site.reverse('webshop_category_list') + '?search=Electronics'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Should find the parent "Electronics" by name and 3 children through parent__name lookup
        self.assertEqual(len(response.context['object_list']), 4)
        self.assertIn(self.parent, response.context['object_list'])
        self.assertIn(self.categories[0], response.context['object_list'])
        self.assertIn(self.categories[1], response.context['object_list'])
        self.assertIn(self.categories[2], response.context['object_list'])

    def test_search_no_query(self):
        """Test that no search query returns all results."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']
            search_fields = ['name']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # No search parameter
        url = site.reverse('webshop_category_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 5)

    def test_search_empty_query(self):
        """Test that empty search query returns all results."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']
            search_fields = ['name']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Empty search parameter
        url = site.reverse('webshop_category_list') + '?search='
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 5)

    def test_search_no_matches(self):
        """Test searching with query that matches nothing."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['name', 'slug']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search for something that doesn't exist
        url = site.reverse('webshop_category_list') + '?search=Nonexistent'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)

    def test_search_partial_match(self):
        """Test that search does partial matching (icontains)."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            search_fields = ['slug']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search for partial slug
        url = site.reverse('webshop_category_list') + '?search=laptop'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.categories[0], response.context['object_list'])  # laptop-computers

    def test_search_widget_displayed(self):
        """Test that search widget appears in sidebar when search_fields configured."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']
            search_fields = ['name']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        url = site.reverse('webshop_category_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Check that search widget is in sidebar_widgets
        sidebar_widgets = response.context.get('sidebar_widgets', [])
        search_widget = next((w for w in sidebar_widgets if w['identifier'] == 'search'), None)
        self.assertIsNotNone(search_widget)
        self.assertEqual(search_widget['template'], 'djadmin/includes/search_widget.html')

    def test_search_preserves_other_params(self):
        """Test that search preserves other query parameters (filters, ordering)."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']
            search_fields = ['name']
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        # Search with ordering parameter
        url = site.reverse('webshop_category_list') + '?search=Computer&ordering=name'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # Both search and ordering should be applied
        results = list(response.context['object_list'])
        self.assertEqual(len(results), 3)  # Search filters to Computer categories
        # Ordering by name: Computer Accessories, Desktop Computers, Laptop Computers
        self.assertEqual(results[0].name, 'Computer Accessories')
        self.assertEqual(results[1].name, 'Desktop Computers')
        self.assertEqual(results[2].name, 'Laptop Computers')


@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestSearchWidgetDisplay(TestCase):
    """Test search widget display logic in isolation."""

    def setUp(self):
        """Set up test data."""
        if site.is_registered(Category):
            site.unregister(Category)

        # Create test categories
        self.parent = CategoryFactory(name='Electronics', slug='electronics', is_active=True)
        self.categories = [
            CategoryFactory(name='Laptop Computers', slug='laptop-computers', parent=self.parent, is_active=True),
            CategoryFactory(name='Office Supplies', slug='office-supplies', parent=None, is_active=True),
        ]

    def tearDown(self):
        """Clean up."""
        if site.is_registered(Category):
            site.unregister(Category)

    def test_search_widget_not_displayed_without_search_fields(self):
        """Test that search widget doesn't appear when no search_fields."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name']
            # No search_fields
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        url = site.reverse('webshop_category_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        sidebar_widgets = response.context.get('sidebar_widgets', [])
        search_widget = next((w for w in sidebar_widgets if w['identifier'] == 'search'), None)
        self.assertIsNone(search_widget)

    def test_search_with_no_search_fields(self):
        """Test that search is ignored when no search_fields configured."""

        class CategoryAdmin(ModelAdmin):
            list_display = ['name', 'slug']
            # No search_fields
            permission_class = None

        site.register(Category, CategoryAdmin, override=True)

        url = site.reverse('webshop_category_list') + '?search=Laptop'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # All categories returned (search ignored)
        self.assertEqual(len(response.context['object_list']), 3)
