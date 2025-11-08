"""Tests for filtering functionality."""

import pytest
from djadmin import ModelAdmin
from djadmin.dataclasses import Column, Filter
from django.test import RequestFactory

from djadmin_filters.filterset_factory import FilterSetFactory


@pytest.fixture
def product_model(db):
    """Get Product model from test models."""
    from tests.test_models import Product

    return Product


@pytest.fixture
def product_admin(product_model):
    """Product ModelAdmin with filter configuration."""
    from djadmin import AdminSite

    class ProductAdmin(ModelAdmin):
        list_display = [
            Column('name', filter=Filter(lookup_expr='icontains')),
            Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            Column('stock', filter=True),  # Boolean normalization
        ]

    site = AdminSite()
    return ProductAdmin(product_model, site)


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


class TestFilterSetFactory:
    """Tests for FilterSetFactory."""

    def test_factory_initialization(self):
        """Test factory can be instantiated."""
        factory = FilterSetFactory()
        assert factory is not None

    def test_create_filterset_with_column_filters(self, product_model, product_admin):
        """Test FilterSet generation from column configuration."""
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, product_admin)

        assert filterset_class is not None
        assert hasattr(filterset_class, 'Meta')
        assert filterset_class.Meta.model == product_model

    def test_create_filterset_without_filters(self, product_model):
        """Test returns None when no filters configured."""
        from djadmin import AdminSite

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),  # No filter
                Column('price'),  # No filter
            ]

        site = AdminSite()
        admin = ProductAdmin(product_model, site)
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, admin)

        assert filterset_class is None

    def test_filterset_has_correct_filters(self, product_model, product_admin):
        """Test generated FilterSet has correct filter fields."""
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, product_admin)

        # Should have filters for name, price, stock
        assert hasattr(filterset_class, 'base_filters')
        filter_names = list(filterset_class.base_filters.keys())

        assert 'name' in filter_names
        assert 'price' in filter_names
        assert 'stock' in filter_names

    def test_custom_filterset_class_used_directly(self, product_model):
        """Test custom filterset_class is used without modification."""
        import django_filters
        from djadmin import AdminSite

        class CustomFilterSet(django_filters.FilterSet):
            custom_filter = django_filters.CharFilter()

            class Meta:
                model = product_model
                fields = ['name']

        class ProductAdmin(ModelAdmin):
            filterset_class = CustomFilterSet
            list_display = [Column('name')]  # No filter config

        site = AdminSite()
        admin = ProductAdmin(product_model, site)
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, admin)

        # Should return the custom class as-is
        assert filterset_class == CustomFilterSet

    def test_custom_filterset_extended_with_columns(self, product_model):
        """Test custom filterset_class extended with column filters."""
        import django_filters
        from djadmin import AdminSite

        class BaseFilterSet(django_filters.FilterSet):
            custom_filter = django_filters.CharFilter()

            class Meta:
                model = product_model
                fields = []

        class ProductAdmin(ModelAdmin):
            filterset_class = BaseFilterSet
            list_display = [
                Column('name', filter=True),  # Add to base class
            ]

        site = AdminSite()
        admin = ProductAdmin(product_model, site)
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, admin)

        # Should be a new class extending BaseFilterSet
        assert filterset_class is not BaseFilterSet
        assert issubclass(filterset_class, BaseFilterSet)

        # Should have both custom_filter and name filter
        assert 'custom_filter' in filterset_class.base_filters
        assert 'name' in filterset_class.base_filters


class TestFilterSetIntegration:
    """Integration tests for FilterSet with QuerySet filtering."""

    @pytest.fixture
    def products(self, db, product_model):
        """Create test products."""
        from tests.factories import ProductFactory

        return [
            ProductFactory(name='Laptop', price=1000, stock=10),
            ProductFactory(name='Mouse', price=25, stock=50),
            ProductFactory(name='Keyboard', price=75, stock=0),
        ]

    def test_filterset_filters_queryset(self, product_model, product_admin, products, request_factory):
        """Test FilterSet actually filters QuerySet."""
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, product_admin)

        # Create filterset with filter data
        request = request_factory.get('/', {'name': 'Laptop'})
        filterset = filterset_class(request.GET, queryset=product_model.objects.all())

        # Should filter to just Laptop
        assert filterset.qs.count() == 1
        assert filterset.qs.first().name == 'Laptop'

    def test_range_filter_works(self, product_model, product_admin, products, request_factory):
        """Test range filter (price__gte, price__lte)."""
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, product_admin)

        # Filter price range 20-100
        request = request_factory.get('/', {'price_min': '20', 'price_max': '100'})
        filterset = filterset_class(request.GET, queryset=product_model.objects.all())

        # Should get Mouse and Keyboard (25 and 75)
        assert filterset.qs.count() == 2
        names = {p.name for p in filterset.qs}
        assert names == {'Mouse', 'Keyboard'}

    def test_multiple_filters_combined(self, product_model, product_admin, products, request_factory):
        """Test multiple filters work together."""
        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(product_model, product_admin)

        # Filter: name contains 'o' AND stock > 0
        # Note: For exact filters, just use the field name with the value
        request = request_factory.get('/', {'name': 'Mouse', 'stock': '50'})
        filterset = filterset_class(request.GET, queryset=product_model.objects.all())

        # Should get just Mouse (exact name match, exact stock)
        result = filterset.qs
        assert result.count() == 1
        assert result.first().name == 'Mouse'
