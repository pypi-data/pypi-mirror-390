from django.apps import AppConfig


class DjAdminFiltersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djadmin_filters'
    verbose_name = 'Django Admin Deux - Filters'

    def ready(self):
        # Register hooks with djadmin plugin system
        from . import djadmin_hooks  # noqa: F401
