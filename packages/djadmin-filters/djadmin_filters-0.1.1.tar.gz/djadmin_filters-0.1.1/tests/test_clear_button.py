"""Tests for clear button visibility with range filters."""

import pytest
from djadmin import Column, ModelAdmin, site
from djadmin.dataclasses import Filter
from django.test import TestCase, override_settings
from django.urls import clear_url_caches

from .factories import ProductFactory
from .test_models import Product


class DynamicURLConf:
    """URLconf that regenerates admin URLs on each access."""

    @property
    def urlpatterns(self):
        from django.urls import include, path

        return [
            path('djadmin/', include(site.urls)),
        ]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=DynamicURLConf())
class TestClearButtonWithRangeFilters(TestCase):
    """Test that clear button shows correctly with range filters."""

    def setUp(self):
        """Set up test data and clean registry."""
        if Product in site._registry:
            site.unregister(Product)

        # Create test products
        self.products = ProductFactory.create_batch(5, price=100)

    def tearDown(self):
        """Clean up registry and URL caches."""
        if Product in site._registry:
            site.unregister(Product)
        clear_url_caches()
        if hasattr(self.client, '_cached_urlconf'):
            delattr(self.client, '_cached_urlconf')

    def test_clear_button_shows_with_range_filter_min_only(self):
        """Test clear button shows when only min value is set in range filter."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),
                Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            ]

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('tests_product_list')

        # Apply only min filter (price_0)
        response = self.client.get(url, {'price_0': '50'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_active_filters'])
        self.assertContains(response, 'Clear')

    def test_clear_button_shows_with_range_filter_max_only(self):
        """Test clear button shows when only max value is set in range filter."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),
                Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            ]

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('tests_product_list')

        # Apply only max filter (price_1)
        response = self.client.get(url, {'price_1': '200'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_active_filters'])
        self.assertContains(response, 'Clear')

    def test_clear_button_shows_with_range_filter_both(self):
        """Test clear button shows when both min and max are set in range filter."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),
                Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            ]

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('tests_product_list')

        # Apply both min and max filters
        response = self.client.get(url, {'price_0': '50', 'price_1': '200'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_active_filters'])
        self.assertContains(response, 'Clear')

    def test_clear_button_hidden_without_filters(self):
        """Test clear button is hidden when no filters are active."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),
                Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            ]

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('tests_product_list')

        # No filters applied
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_active_filters'])
        self.assertNotContains(response, 'Clear')

    def test_clear_url_removes_range_filter_params(self):
        """Test that clear_filters_url removes both price_0 and price_1 parameters."""

        class ProductAdmin(ModelAdmin):
            list_display = [
                Column('name'),
                Column('price', filter=Filter(lookup_expr=['gte', 'lte'])),
            ]

        site.register(Product, ProductAdmin, override=True)
        url = site.reverse('tests_product_list')

        # Apply filters with search and ordering
        response = self.client.get(url, {'price_0': '50', 'price_1': '200', 'search': 'test', 'ordering': 'name'})

        self.assertEqual(response.status_code, 200)

        # Check that clear_filters_url removes price_0 and price_1 but keeps search and ordering
        clear_url = response.context['clear_filters_url']
        self.assertIn('search=test', clear_url)
        self.assertIn('ordering=name', clear_url)
        self.assertNotIn('price_0', clear_url)
        self.assertNotIn('price_1', clear_url)
