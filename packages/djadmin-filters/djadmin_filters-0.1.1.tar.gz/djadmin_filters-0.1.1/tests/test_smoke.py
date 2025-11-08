"""Smoke tests to verify plugin loads correctly."""

import pytest


def test_plugin_loads():
    """Test that the plugin can be imported."""
    import djadmin_filters

    assert djadmin_filters.__version__ == '0.1.0'


def test_dataclasses_importable():
    """Test that Filter and Order can be imported from djadmin."""
    from djadmin import Filter, Order

    assert Filter is not None
    assert Order is not None

    # Also test they can be imported from djadmin_filters (re-export)
    from djadmin_filters import Filter as F2
    from djadmin_filters import Order as O2

    assert F2 is Filter
    assert O2 is Order


def test_filter_dataclass():
    """Test Filter dataclass basic functionality."""
    from djadmin import Filter

    # Default filter
    f = Filter()
    assert f.lookup_expr == 'exact'
    assert f.exclude is False
    assert f.distinct is False

    # Custom filter
    f = Filter(lookup_expr='icontains', label='Search')
    assert f.lookup_expr == 'icontains'
    assert f.label == 'Search'

    # to_kwargs conversion
    kwargs = f.to_kwargs()
    assert 'lookup_expr' in kwargs
    assert 'label' in kwargs


def test_order_dataclass():
    """Test Order dataclass basic functionality."""
    from djadmin import Order

    # Default order
    o = Order()
    assert o.enabled is True
    assert o.fields is None

    # Disabled order
    o = Order(enabled=False)
    assert o.enabled is False

    # to_ordering_choice conversion
    o = Order()
    choice = o.to_ordering_choice('name', 'Name')
    assert choice is not None
    assert len(choice) == 2
    assert choice[0] == ('name', 'Name')
    assert choice[1] == ('-name', 'Name (desc)')

    # Disabled order returns None
    o = Order(enabled=False)
    choice = o.to_ordering_choice('name', 'Name')
    assert choice is None


@pytest.mark.django_db
def test_hooks_registered():
    """Test that plugin hooks are registered with djadmin."""
    from djadmin.plugins import pm

    # Get all features from all plugins
    features = pm.hook.djadmin_provides_features()
    all_features = [f for fs in features for f in fs]

    # Our plugin should advertise filter, ordering, and search
    assert 'filter' in all_features
    assert 'ordering' in all_features
    assert 'search' in all_features


@pytest.mark.django_db
def test_column_filter_order_attributes():
    """Test that Column class has filter and order attributes."""
    from djadmin import Column

    # Column should have filter and order attributes
    col = Column('name')
    assert hasattr(col, 'filter')
    assert hasattr(col, 'order')

    # Default values
    assert col.filter is None
    assert col.order is None

    # With filter/order
    col = Column('name', filter=True, order=True)
    assert col.filter is True
    assert col.order is True
