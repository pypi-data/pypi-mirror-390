"""Mixins for ListView to add filtering, ordering, and search capabilities."""

from django_filters.views import FilterMixin


class DjAdminFiltersMixin(FilterMixin):
    """
    Mixin for ListView actions to add filtering, ordering, and search.

    This mixin extends django-filter's FilterMixin and is injected into
    ListViewAction by the plugin system. It uses FilterSetFactory to generate
    FilterSet classes from ModelAdmin column configuration.

    Features:
        - Filtering via django-filter (Phase 1) ✅
        - Ordering via OrderingFilter (Phase 2) 🚧
        - Search across multiple fields (Phase 3) 🚧

    The mixin integrates with Django's ListView pattern and provides:
        - get_filterset_class() - Generate or return FilterSet
        - get_filterset() - Instantiate FilterSet with request data
        - get_queryset() - Apply filters to queryset
    """

    # FilterSet configuration
    filterset_class = None  # Will be generated from ModelAdmin config

    def get_filterset_class(self):
        """
        Get or generate the FilterSet class for this view.

        This method checks model_admin configuration and uses FilterSetFactory
        to generate an appropriate FilterSet class.

        Returns:
            FilterSet class, or None if no filters configured
        """
        # Check if already cached
        if self.filterset_class is not None:
            return self.filterset_class

        # Generate from ModelAdmin configuration
        from .filterset_factory import FilterSetFactory

        factory = FilterSetFactory()
        filterset_class = factory.create_filterset(model=self.model, model_admin=self.model_admin)

        return filterset_class

    def get_filterset(self, filterset_class):
        """
        Instantiate the FilterSet with request data.

        Args:
            filterset_class: The FilterSet class to instantiate

        Returns:
            FilterSet instance, or None if no filterset_class
        """
        if filterset_class is None:
            return None

        # Get the base queryset
        queryset = self.get_queryset_for_filter()

        # Instantiate FilterSet with request GET data
        return filterset_class(self.request.GET, queryset=queryset, request=self.request)

    def get_queryset_for_filter(self):
        """
        Get the base queryset to be filtered.

        This method gets the queryset before filtering is applied,
        allowing parent classes to modify it first.

        Returns:
            QuerySet to be filtered
        """
        # Call super to get the base queryset with any modifications
        # from other mixins or the action
        if hasattr(super(), 'get_queryset'):
            return super().get_queryset()

        # Fallback to model's default manager
        return self.model._default_manager.all()

    def get_queryset(self):
        """
        Get the filtered queryset for the ListView.

        This overrides ListView's get_queryset() to apply filtering and ordering.

        Returns:
            Filtered QuerySet
        """
        # Get the FilterSet class
        filterset_class = self.get_filterset_class()

        if filterset_class is None:
            # No filters configured, just apply ordering
            queryset = self.get_queryset_for_filter()
            return self._apply_ordering(queryset)

        # Get the FilterSet instance
        self.filterset = self.get_filterset(filterset_class)

        if self.filterset is None:
            queryset = self.get_queryset_for_filter()
            return self._apply_ordering(queryset)

        # Apply ordering to filtered queryset
        return self._apply_ordering(self.filterset.qs)

    def _apply_ordering(self, queryset):
        """
        Apply ordering from URL parameter to queryset.

        Args:
            queryset: The queryset to order

        Returns:
            Ordered queryset
        """
        from djadmin.dataclasses import Column

        ordering_param = self.request.GET.get('ordering')
        if not ordering_param:
            return queryset

        # Validate that the ordering field is allowed
        allowed_fields = set()
        for column in self.model_admin.list_display:
            if isinstance(column, Column) and column.order and isinstance(column.field, str):
                allowed_fields.add(column.field)
                allowed_fields.add(f'-{column.field}')

        if ordering_param not in allowed_fields:
            # Invalid ordering field, ignore it
            return queryset

        return queryset.order_by(ordering_param)

    def get_context_data(self, **kwargs):
        """
        Add FilterSet to template context.

        Returns:
            Context dict with 'filterset' added
        """
        context = super().get_context_data(**kwargs)

        # Add filterset to context if it exists
        if hasattr(self, 'filterset'):
            context['filterset'] = self.filterset

            # Check if any filter fields have values (excluding search/ordering/page)
            # This helps templates show/hide the clear button appropriately
            context['has_active_filters'] = self._has_active_filters()

            # Provide a clean URL for clearing filters (keeps search and ordering)
            context['clear_filters_url'] = self._get_clear_filters_url()

        return context

    def _has_active_filters(self):
        """
        Check if any filter fields have active values.

        This excludes non-filter parameters like 'search', 'ordering', 'page', etc.

        Returns:
            bool: True if any filter field has a value, False otherwise
        """
        if not hasattr(self, 'filterset') or self.filterset is None:
            return False

        if not hasattr(self.filterset, 'form') or self.filterset.form is None:
            return False

        # Check if any filter parameters exist in request.GET with non-empty values
        # We simply check if any parameters in request.GET match filter field names
        # The form's data dict contains all the parameters it consumed from request.GET
        if self.filterset.form.data:
            # Iterate through all GET parameters
            for param_name, values in self.filterset.form.data.lists():
                # Check if this parameter corresponds to a filter field
                # by checking if it starts with any of our field names
                for field_name in self.filterset.form.fields.keys():
                    if param_name == field_name or param_name.startswith(f'{field_name}_'):
                        # Found a filter parameter, check if it has a non-empty value
                        for value in values:
                            if value and value not in ('', '---------'):
                                return True

        return False

    def _get_clear_filters_url(self):
        """
        Build a URL that clears all filters but preserves all other parameters.

        This method removes only filter field parameters and page,
        preserving any other query parameters that might be added by other plugins.

        Returns:
            str: Query string with filter parameters removed
        """
        from urllib.parse import urlencode

        if not hasattr(self, 'filterset') or self.filterset is None:
            return '?'

        if not hasattr(self.filterset, 'form') or self.filterset.form is None:
            return '?'

        # Get all GET parameter names used by the filter form
        # The form's data dict knows exactly which parameters it uses
        filter_param_names = set()

        if self.filterset.form.data:
            # Get all parameter names that the form consumed from request.GET
            for param_name in self.filterset.form.data.keys():
                # Check if this parameter belongs to one of our filter fields
                for field_name in self.filterset.form.fields.keys():
                    if param_name == field_name or param_name.startswith(f'{field_name}_'):
                        filter_param_names.add(param_name)
                        break

        # Build a dict of all parameters EXCEPT filter fields and page
        preserved_params = {}
        for key in self.request.GET:
            if key not in filter_param_names and key != 'page':
                # Handle multiple values for the same key
                values = self.request.GET.getlist(key)
                if len(values) == 1:
                    preserved_params[key] = values[0]
                else:
                    preserved_params[key] = values

        # Build query string
        if preserved_params:
            return '?' + urlencode(preserved_params, doseq=True)
        return '?'
