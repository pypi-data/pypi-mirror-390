"""Tests for ordering functionality."""

import pytest
from djadmin import AdminSite, ModelAdmin
from djadmin.dataclasses import Column, Order
from django.test import RequestFactory


@pytest.fixture
def product_model(db):
    """Get Product model from test models."""
    from tests.test_models import Product

    return Product


@pytest.fixture
def product_admin_with_ordering(product_model):
    """Product ModelAdmin with ordering configuration."""

    class ProductAdmin(ModelAdmin):
        list_display = [
            Column('name', order=Order()),
            Column('price', order=Order()),
            Column('stock', order=True),  # Boolean normalization
            Column('description', order=Order(enabled=False)),  # Disabled
        ]

    site = AdminSite()
    return ProductAdmin(product_model, site)


@pytest.fixture
def request_factory():
    """Request factory for creating mock requests."""
    return RequestFactory()


@pytest.fixture
def products(db, product_model):
    """Create test products."""
    from tests.factories import ProductFactory

    return [
        ProductFactory(name='Zebra Widget', price=100, stock=5),
        ProductFactory(name='Alpha Product', price=50, stock=10),
        ProductFactory(name='Beta Item', price=75, stock=3),
    ]


class TestOrderingMixin:
    """Tests for DjAdminFiltersMixin ordering functionality."""

    def test_ordering_by_name_ascending(self, product_model, product_admin_with_ordering, products, request_factory):
        """Test ordering by name in ascending order."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        # Create a minimal view-like object
        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

            def get_queryset_for_filter(self):
                return product_model.objects.all()

        view = MockView()
        view.request = request_factory.get('/', {'ordering': 'name'})

        queryset = view._apply_ordering(product_model.objects.all())

        # Should be ordered alphabetically
        names = [p.name for p in queryset]
        assert names == ['Alpha Product', 'Beta Item', 'Zebra Widget']

    def test_ordering_by_name_descending(self, product_model, product_admin_with_ordering, products, request_factory):
        """Test ordering by name in descending order."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

            def get_queryset_for_filter(self):
                return product_model.objects.all()

        view = MockView()
        view.request = request_factory.get('/', {'ordering': '-name'})

        queryset = view._apply_ordering(product_model.objects.all())

        # Should be ordered reverse alphabetically
        names = [p.name for p in queryset]
        assert names == ['Zebra Widget', 'Beta Item', 'Alpha Product']

    def test_ordering_by_price(self, product_model, product_admin_with_ordering, products, request_factory):
        """Test ordering by price."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

        view = MockView()
        view.request = request_factory.get('/', {'ordering': 'price'})

        queryset = view._apply_ordering(product_model.objects.all())

        # Should be ordered by price (50, 75, 100)
        prices = [p.price for p in queryset]
        assert prices == [50, 75, 100]

    def test_ordering_rejects_invalid_field(
        self, product_model, product_admin_with_ordering, products, request_factory
    ):
        """Test ordering with invalid field name is ignored."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

        view = MockView()
        view.request = request_factory.get('/', {'ordering': 'invalid_field'})

        # Should ignore invalid ordering and return unordered
        queryset = view._apply_ordering(product_model.objects.all())
        assert queryset.count() == 3

    def test_ordering_rejects_disabled_field(
        self, product_model, product_admin_with_ordering, products, request_factory
    ):
        """Test ordering with disabled field is rejected."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

        view = MockView()
        # description has order=Order(enabled=False)
        view.request = request_factory.get('/', {'ordering': 'description'})

        queryset = view._apply_ordering(product_model.objects.all())
        # Should ignore disabled field
        assert queryset.count() == 3

    def test_no_ordering_parameter_returns_unchanged(
        self, product_model, product_admin_with_ordering, products, request_factory
    ):
        """Test queryset unchanged when no ordering parameter."""
        from djadmin_filters.mixins import DjAdminFiltersMixin

        class MockView(DjAdminFiltersMixin):
            model = product_model
            model_admin = product_admin_with_ordering

        view = MockView()
        view.request = request_factory.get('/')  # No ordering param

        queryset = view._apply_ordering(product_model.objects.all())
        assert queryset.count() == 3


class TestColumnHeaderIcons:
    """Tests for column header icon rendering."""

    def test_sort_icon_template_for_unsorted_column(self, product_admin_with_ordering, request_factory):
        """Test sort icon shows neutral state for unsorted column."""
        from djadmin_filters.djadmin_hooks import get_sort_icon_template

        column = Column('name', order=Order())
        request = request_factory.get('/')  # No ordering

        template = get_sort_icon_template(column, request)
        assert template == 'djadmin/icons/sort.html'

    def test_sort_icon_template_for_ascending_column(self, product_admin_with_ordering, request_factory):
        """Test sort icon shows up arrow for ascending sort."""
        from djadmin_filters.djadmin_hooks import get_sort_icon_template

        column = Column('name', order=Order())
        request = request_factory.get('/', {'ordering': 'name'})

        template = get_sort_icon_template(column, request)
        assert template == 'djadmin/icons/sort-up.html'

    def test_sort_icon_template_for_descending_column(self, product_admin_with_ordering, request_factory):
        """Test sort icon shows down arrow for descending sort."""
        from djadmin_filters.djadmin_hooks import get_sort_icon_template

        column = Column('name', order=Order())
        request = request_factory.get('/', {'ordering': '-name'})

        template = get_sort_icon_template(column, request)
        assert template == 'djadmin/icons/sort-down.html'

    def test_sort_url_for_unsorted_column(self, request_factory):
        """Test sort URL for unsorted column links to ascending sort."""
        from djadmin_filters.djadmin_hooks import get_sort_url

        column = Column('name', order=Order())
        request = request_factory.get('/')

        url = get_sort_url(column, request)
        assert 'ordering=name' in url

    def test_sort_url_for_ascending_column(self, request_factory):
        """Test sort URL for ascending column links to descending sort."""
        from djadmin_filters.djadmin_hooks import get_sort_url

        column = Column('name', order=Order())
        request = request_factory.get('/', {'ordering': 'name'})

        url = get_sort_url(column, request)
        assert 'ordering=-name' in url

    def test_sort_url_for_descending_column(self, request_factory):
        """Test sort URL for descending column toggles back to ascending."""
        from djadmin_filters.djadmin_hooks import get_sort_url

        column = Column('name', order=Order())
        request = request_factory.get('/', {'ordering': '-name'})

        url = get_sort_url(column, request)
        assert 'ordering=name' in url  # Toggle back to ascending

    def test_sort_url_preserves_other_params(self, request_factory):
        """Test sort URL preserves other query parameters."""
        from djadmin_filters.djadmin_hooks import get_sort_url

        column = Column('name', order=Order())
        request = request_factory.get('/', {'ordering': 'name', 'page': '2', 'filter': 'active'})

        url = get_sort_url(column, request)
        assert 'page=2' in url
        assert 'filter=active' in url

    def test_sort_icon_should_display_for_orderable_column(self, request_factory):
        """Test sort icon displays for columns with order=True."""
        from djadmin_filters.djadmin_hooks import should_display_sort_icon

        column = Column('name', order=Order())
        request = request_factory.get('/')

        assert should_display_sort_icon(column, request) is True

    def test_sort_icon_should_not_display_for_disabled_column(self, request_factory):
        """Test sort icon does not display for disabled ordering."""
        from djadmin_filters.djadmin_hooks import should_display_sort_icon

        column = Column('name', order=Order(enabled=False))
        request = request_factory.get('/')

        assert should_display_sort_icon(column, request) is False

    def test_sort_icon_should_not_display_without_order(self, request_factory):
        """Test sort icon does not display without order config."""
        from djadmin_filters.djadmin_hooks import should_display_sort_icon

        column = Column('name')  # No order
        request = request_factory.get('/')

        assert should_display_sort_icon(column, request) is False

    def test_sort_title_for_unsorted_column(self, request_factory):
        """Test sort title for unsorted column."""
        from djadmin_filters.djadmin_hooks import get_sort_title

        column = Column('name', label='Product Name', order=Order())
        request = request_factory.get('/')

        title = get_sort_title(column, request)
        assert 'Click to sort by Product Name' in title

    def test_sort_title_for_ascending_column(self, request_factory):
        """Test sort title for ascending column."""
        from djadmin_filters.djadmin_hooks import get_sort_title

        column = Column('name', label='Product Name', order=Order())
        request = request_factory.get('/', {'ordering': 'name'})

        title = get_sort_title(column, request)
        assert 'ascending' in title.lower()
        assert 'descending' in title.lower()

    def test_sort_title_for_descending_column(self, request_factory):
        """Test sort title for descending column."""
        from djadmin_filters.djadmin_hooks import get_sort_title

        column = Column('name', label='Product Name', order=Order())
        request = request_factory.get('/', {'ordering': '-name'})

        title = get_sort_title(column, request)
        assert 'descending' in title.lower()
        assert 'ascending' in title.lower()  # Should toggle back to ascending


class TestOrderDataclass:
    """Tests for Order dataclass."""

    def test_order_enabled_by_default(self):
        """Test Order is enabled by default."""
        order = Order()
        assert order.enabled is True
        assert bool(order) is True

    def test_order_can_be_disabled(self):
        """Test Order can be disabled."""
        order = Order(enabled=False)
        assert order.enabled is False
        assert bool(order) is False

    def test_order_to_ordering_choice(self):
        """Test Order.to_ordering_choice generates choices."""
        order = Order(label='Name (A-Z)', descending_label='Name (Z-A)')
        choices = order.to_ordering_choice('name', 'Name')

        assert choices == (('name', 'Name (A-Z)'), ('-name', 'Name (Z-A)'))

    def test_order_to_ordering_choice_with_defaults(self):
        """Test Order.to_ordering_choice with default labels."""
        order = Order()
        choices = order.to_ordering_choice('price', 'Price')

        assert choices == (('price', 'Price'), ('-price', 'Price (desc)'))

    def test_order_to_ordering_choice_disabled(self):
        """Test Order.to_ordering_choice returns None when disabled."""
        order = Order(enabled=False)
        choices = order.to_ordering_choice('name', 'Name')

        assert choices is None
