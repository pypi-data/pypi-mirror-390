"""Django-filter integration for django-admin-deux."""

__version__ = '0.1.1'

# Re-export Filter and Order from djadmin for convenience
from djadmin import Filter, Order

# Default Django app configuration
default_app_config = 'djadmin_filters.apps.DjAdminFiltersConfig'

__all__ = ['Filter', 'Order']
