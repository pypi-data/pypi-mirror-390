"""Tests for filter/order normalization in ModelAdmin metaclass."""

import pytest


@pytest.mark.django_db
def test_boolean_filter_normalization():
    """Test that filter=True/False is normalized to Filter()/None."""
    from djadmin import Column, Filter, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('name', filter=True),
            Column('description', filter=False),
        ]

    # filter=True should be normalized to Filter()
    assert isinstance(TestAdmin.list_display[0].filter, Filter)

    # filter=False should be normalized to None
    assert TestAdmin.list_display[1].filter is None


@pytest.mark.django_db
def test_boolean_order_normalization():
    """Test that order=True/False is normalized to Order()."""
    from djadmin import Column, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('name', order=True),
            Column('description', order=False),
        ]

    # order=True should be normalized to Order()
    assert isinstance(TestAdmin.list_display[0].order, Order)
    assert TestAdmin.list_display[0].order.enabled is True

    # order=False should be normalized to Order(enabled=False)
    assert isinstance(TestAdmin.list_display[1].order, Order)
    assert TestAdmin.list_display[1].order.enabled is False


@pytest.mark.django_db
def test_order_none_defaults_to_disabled():
    """Test that order=None defaults to Order(enabled=False)."""
    from djadmin import Column, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('name'),  # order=None
        ]

    # order=None should default to Order(enabled=False)
    assert isinstance(TestAdmin.list_display[0].order, Order)
    assert TestAdmin.list_display[0].order.enabled is False


@pytest.mark.django_db
def test_explicit_filter_order_objects():
    """Test that explicit Filter/Order objects are preserved."""
    from djadmin import Column, Filter, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('name', filter=Filter(lookup_expr='icontains'), order=Order(label='Name (A-Z)')),
        ]

    # Explicit objects should be preserved
    assert isinstance(TestAdmin.list_display[0].filter, Filter)
    assert TestAdmin.list_display[0].filter.lookup_expr == 'icontains'

    assert isinstance(TestAdmin.list_display[0].order, Order)
    assert TestAdmin.list_display[0].order.label == 'Name (A-Z)'


@pytest.mark.django_db
def test_legacy_list_filter_normalization():
    """Test that list_filter is normalized to Column.filter."""
    from djadmin import Filter, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = ['name', 'status']
        list_filter = ['status']

    # status should have filter applied
    status_col = [col for col in TestAdmin.list_display if col.field == 'status'][0]
    assert isinstance(status_col.filter, Filter)

    # name should not have filter (not in list_filter)
    name_col = [col for col in TestAdmin.list_display if col.field == 'name'][0]
    # Note: name will have Order() due to default, but filter should be None
    # Actually, looking at the metaclass, filter won't be touched if not boolean
    # So we need to check if it's still None or was set to Filter
    # The legacy normalization only adds filter if col.filter is None
    # So name_col.filter should still be None after normalization
    assert name_col.filter is None


@pytest.mark.django_db
def test_legacy_list_filter_with_lookup():
    """Test that list_filter with lookup expressions is normalized."""
    from djadmin import Filter, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = ['price']
        list_filter = [('price', ['gte', 'lte'])]

    # price should have filter with lookup_expr=['gte', 'lte']
    price_col = TestAdmin.list_display[0]
    assert isinstance(price_col.filter, Filter)
    assert price_col.filter.lookup_expr == ['gte', 'lte']


@pytest.mark.django_db
def test_legacy_order_fields_normalization():
    """Test that order_fields is normalized to Column.order."""
    from djadmin import ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = ['name', 'description']
        order_fields = ['name']

    # name should have order enabled (via order_fields)
    name_col = [col for col in TestAdmin.list_display if col.field == 'name'][0]
    assert isinstance(name_col.order, Order)
    assert name_col.order.enabled is True

    # description should have Order(enabled=False) (default, not in order_fields)
    desc_col = [col for col in TestAdmin.list_display if col.field == 'description'][0]
    assert isinstance(desc_col.order, Order)
    assert desc_col.order.enabled is False


@pytest.mark.django_db
def test_mixed_configuration():
    """Test mixing Column objects, strings, and legacy attributes."""
    from djadmin import Column, Filter, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            'name',  # Plain string
            Column('sku', filter=True),  # Column with boolean
            Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),  # Column with object
        ]
        list_filter = ['name']  # Legacy
        order_fields = ['name', 'price']  # Legacy

    # name: string, should have filter from list_filter
    name_col = [col for col in TestAdmin.list_display if col.field == 'name'][0]
    assert isinstance(name_col.filter, Filter)

    # sku: Column with filter=True, should be normalized
    sku_col = [col for col in TestAdmin.list_display if col.field == 'sku'][0]
    assert isinstance(sku_col.filter, Filter)

    # price: Column with explicit Filter, should be preserved
    price_col = [col for col in TestAdmin.list_display if col.field == 'price'][0]
    assert isinstance(price_col.filter, Filter)
    assert price_col.filter.lookup_expr == ['gte', 'lte']

    # All should have Order (normalized)
    assert all(isinstance(col.order, Order) for col in TestAdmin.list_display)
    # name and price should be enabled via order_fields, others disabled
    assert name_col.order.enabled is True
    assert price_col.order.enabled is True
    assert sku_col.order.enabled is False
