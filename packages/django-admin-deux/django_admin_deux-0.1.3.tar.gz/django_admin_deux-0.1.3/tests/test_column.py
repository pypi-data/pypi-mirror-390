"""Tests for Column dataclass and list_display functionality"""

import pytest

from djadmin import Column, ModelAdmin
from djadmin.templatetags.djadmin_tags import get_column_label, get_column_value
from examples.webshop.factories import CategoryFactory, ProductFactory
from examples.webshop.models import Product


def test_column_from_string():
    """Column.from_field should create Column from string"""
    column = Column.from_field('name')

    assert isinstance(column, Column)
    assert column.field == 'name'
    assert column.label is None
    assert column.empty_value == '-'
    assert column.classes == ''


def test_column_from_callable():
    """Column.from_field should create Column from callable"""

    def custom_func(obj):
        return obj.name

    column = Column.from_field(custom_func)

    assert isinstance(column, Column)
    assert column.field == custom_func
    assert column.label is None


def test_column_from_column():
    """Column.from_field should return Column as-is"""
    original = Column('name', label='Product Name')
    column = Column.from_field(original)

    assert column is original


def test_column_field_name_string():
    """Column.field_name should return string field"""
    column = Column('name')
    assert column.field_name == 'name'


def test_column_field_name_callable():
    """Column.field_name should return callable's __name__"""

    def custom_func(obj):
        return obj.name

    column = Column(custom_func)
    assert column.field_name == 'custom_func'


def test_column_field_label_with_label():
    """Column.field_label should return label if set"""
    column = Column('name', label='Product Name')
    assert column.field_label == 'Product Name'


def test_column_field_label_without_label():
    """Column.field_label should return field_name if label not set"""
    column = Column('name')
    assert column.field_label == 'name'


def test_modeladmin_metaclass_normalizes_strings():
    """ModelAdmin metaclass should normalize list_display strings to Columns"""

    class ProductAdmin(ModelAdmin):
        list_display = ['name', 'sku', 'price']

    # Check that list_display was normalized
    assert len(ProductAdmin.list_display) == 3
    assert all(isinstance(col, Column) for col in ProductAdmin.list_display)

    # Check field values
    assert ProductAdmin.list_display[0].field == 'name'
    assert ProductAdmin.list_display[1].field == 'sku'
    assert ProductAdmin.list_display[2].field == 'price'


def test_modeladmin_metaclass_normalizes_callables():
    """ModelAdmin metaclass should normalize callables to Columns"""

    def price_display(obj):
        return f'${obj.price}'

    class ProductAdmin(ModelAdmin):
        list_display = ['name', price_display]

    assert len(ProductAdmin.list_display) == 2
    assert all(isinstance(col, Column) for col in ProductAdmin.list_display)
    assert ProductAdmin.list_display[1].field == price_display


def test_modeladmin_metaclass_preserves_columns():
    """ModelAdmin metaclass should preserve Column objects"""

    class ProductAdmin(ModelAdmin):
        list_display = [
            'name',
            Column('sku', label='SKU Code'),
            Column('price', classes='text-right'),
        ]

    assert len(ProductAdmin.list_display) == 3
    assert all(isinstance(col, Column) for col in ProductAdmin.list_display)

    # First is normalized from string
    assert ProductAdmin.list_display[0].field == 'name'
    assert ProductAdmin.list_display[0].label is None

    # Second preserves custom label
    assert ProductAdmin.list_display[1].field == 'sku'
    assert ProductAdmin.list_display[1].label == 'SKU Code'

    # Third preserves custom classes
    assert ProductAdmin.list_display[2].field == 'price'
    assert ProductAdmin.list_display[2].classes == 'text-right'


def test_modeladmin_metaclass_mixed_style():
    """ModelAdmin metaclass should handle mixed styles"""

    def custom_method(obj):
        return 'custom'

    class ProductAdmin(ModelAdmin):
        list_display = [
            'name',  # String
            Column('sku', label='SKU'),  # Column object
            custom_method,  # Callable
        ]

    assert len(ProductAdmin.list_display) == 3
    assert all(isinstance(col, Column) for col in ProductAdmin.list_display)


@pytest.mark.django_db
def test_get_column_value_simple_field():
    """get_column_value should retrieve simple field values"""
    product = ProductFactory(name='Test Product', sku='TEST-001')

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('name')

    value = get_column_value(product, column, admin)
    assert value == 'Test Product'


@pytest.mark.django_db
def test_get_column_value_related_field():
    """get_column_value should handle related field lookups"""
    category = CategoryFactory(name='Electronics')
    product = ProductFactory(category=category)

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('category__name')

    value = get_column_value(product, column, admin)
    assert value == 'Electronics'


@pytest.mark.django_db
def test_get_column_value_property():
    """get_column_value should handle model properties"""
    product = ProductFactory(stock_quantity=10)

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('is_in_stock')

    value = get_column_value(product, column, admin)
    assert value is True


@pytest.mark.django_db
def test_get_column_value_callable():
    """get_column_value should handle callable"""
    product = ProductFactory(price=100)

    def price_display(obj):
        return f'${obj.price:.2f}'

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column(price_display)

    value = get_column_value(product, column, admin)
    assert value == '$100.00'


@pytest.mark.django_db
def test_get_column_value_admin_method():
    """get_column_value should handle ModelAdmin methods"""
    product = ProductFactory(price=100, cost=60)

    class ProductAdmin(ModelAdmin):
        def profit_display(self, obj):
            return f'${obj.price - obj.cost:.2f}'

    admin = ProductAdmin(Product, None)
    column = Column('profit_display')

    value = get_column_value(product, column, admin)
    assert value == '$40.00'


@pytest.mark.django_db
def test_get_column_value_empty():
    """get_column_value should use empty_value for None/empty string"""
    product = ProductFactory()
    product.short_description = ''  # Empty string
    product.save()

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('short_description', empty_value='N/A')

    value = get_column_value(product, column, admin)
    assert value == 'N/A'


@pytest.mark.django_db
def test_get_column_label_simple():
    """get_column_label should return field verbose_name"""

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('name')

    label = get_column_label(column, Product, admin)
    assert label == 'Name'


@pytest.mark.django_db
def test_get_column_label_custom():
    """get_column_label should use Column.label if provided"""

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('sku', label='SKU Code')

    label = get_column_label(column, Product, admin)
    assert label == 'SKU Code'


@pytest.mark.django_db
def test_get_column_label_callable():
    """get_column_label should use short_description on callable"""

    def price_display(obj):
        return f'${obj.price}'

    price_display.short_description = 'Price (USD)'

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column(price_display)

    label = get_column_label(column, Product, admin)
    assert label == 'Price (USD)'


@pytest.mark.django_db
def test_get_column_label_admin_method():
    """get_column_label should use short_description on admin method"""

    class ProductAdmin(ModelAdmin):
        def profit_display(self, obj):
            return f'${obj.price - obj.cost}'

        profit_display.short_description = 'Profit'

    admin = ProductAdmin(Product, None)
    column = Column('profit_display')

    label = get_column_label(column, Product, admin)
    assert label == 'Profit'


@pytest.mark.django_db
def test_get_column_label_str():
    """get_column_label should handle __str__ specially"""

    class ProductAdmin(ModelAdmin):
        pass

    admin = ProductAdmin(Product, None)
    column = Column('__str__')

    label = get_column_label(column, Product, admin)
    assert label == 'Product'  # Model's verbose_name
