"""Tests for feature advertising with column-centric configuration."""

import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_column_filter_advertises_filter_feature():
    """Test that Column.filter triggers 'filter' feature."""
    from djadmin import Column, Filter, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', filter=Filter()),
        ]

    admin = TestAdmin(User, None)
    assert 'filter' in admin.requested_features


@pytest.mark.django_db
def test_column_filter_boolean_advertises_filter_feature():
    """Test that Column.filter=True (normalized) triggers 'filter' feature."""
    from djadmin import Column, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', filter=True),
        ]

    admin = TestAdmin(User, None)
    assert 'filter' in admin.requested_features


@pytest.mark.django_db
def test_column_order_advertises_ordering_feature():
    """Test that Column.order with enabled=True triggers 'ordering' feature."""
    from djadmin import Column, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', order=Order(enabled=True)),
        ]

    admin = TestAdmin(User, None)
    assert 'ordering' in admin.requested_features


@pytest.mark.django_db
def test_column_order_boolean_advertises_ordering_feature():
    """Test that Column.order=True (normalized) triggers 'ordering' feature."""
    from djadmin import Column, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', order=True),
        ]

    admin = TestAdmin(User, None)
    assert 'ordering' in admin.requested_features


@pytest.mark.django_db
def test_column_order_disabled_does_not_advertise():
    """Test that Column.order with enabled=False does NOT trigger 'ordering' feature."""
    from djadmin import Column, ModelAdmin, Order

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', order=Order(enabled=False)),
        ]

    admin = TestAdmin(User, None)
    assert 'ordering' not in admin.requested_features


@pytest.mark.django_db
def test_column_order_false_does_not_advertise():
    """Test that Column.order=False (normalized) does NOT trigger 'ordering' feature."""
    from djadmin import Column, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username', order=False),
        ]

    admin = TestAdmin(User, None)
    assert 'ordering' not in admin.requested_features


@pytest.mark.django_db
def test_no_filter_or_order_no_features():
    """Test that columns without filter/order don't advertise features."""
    from djadmin import Column, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            Column('username'),
        ]

    admin = TestAdmin(User, None)
    # Default order=None becomes Order(enabled=False), so no features advertised
    assert 'filter' not in admin.requested_features
    assert 'ordering' not in admin.requested_features


@pytest.mark.django_db
def test_legacy_list_filter_still_works():
    """Test that legacy list_filter still triggers 'filter' feature."""
    from djadmin import ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = ['username']
        list_filter = ['is_active']

    admin = TestAdmin(User, None)
    assert 'filter' in admin.requested_features


@pytest.mark.django_db
def test_mixed_legacy_and_column_centric():
    """Test that both legacy and column-centric config work together."""
    from djadmin import Column, ModelAdmin

    class TestAdmin(ModelAdmin):
        list_display = [
            'username',
            Column('email', filter=True),
        ]
        list_filter = ['is_active']  # Legacy

    admin = TestAdmin(User, None)
    assert 'filter' in admin.requested_features
    assert 'ordering' not in admin.requested_features  # No order_fields, defaults to disabled


@pytest.mark.django_db
def test_order_truthy_when_enabled():
    """Test that Order instance is truthy when enabled."""
    from djadmin import Order

    o = Order(enabled=True)
    assert bool(o) is True
    assert o  # Direct truthiness check

    o = Order(enabled=False)
    assert bool(o) is False
    assert not o  # Direct truthiness check
