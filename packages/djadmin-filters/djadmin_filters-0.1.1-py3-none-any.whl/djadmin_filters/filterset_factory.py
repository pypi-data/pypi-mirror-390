"""FilterSet factory for generating django-filter FilterSet classes."""

import django_filters
from django.db import models


class FilterSetFactory:
    """
    Factory for generating django-filter FilterSet classes from ModelAdmin configuration.

    This factory follows the same pattern as ViewFactory, using class-based generation
    with support for base classes, custom methods, and plugin extensibility.

    Example:
        >>> factory = FilterSetFactory()
        >>> filterset_class = factory.create_filterset(Product, product_admin)
        >>> filterset = filterset_class(request.GET, queryset=Product.objects.all())
    """

    def create_filterset(self, model: type[models.Model], model_admin) -> type[django_filters.FilterSet] | None:
        """
        Create a FilterSet class for the given model and ModelAdmin.

        Args:
            model: The Django model class
            model_admin: The ModelAdmin instance with configuration

        Returns:
            A FilterSet class, or None if no filters configured

        Decision Flow:
            1. If model_admin.filterset_class exists AND no column filters → use as-is
            2. If column filters exist → generate new class (may inherit from filterset_class)
            3. If no filters at all → return None
        """
        # Check for custom filterset_class
        base_class = getattr(model_admin, 'filterset_class', None)

        # Check if we have column-based filters
        has_column_filters = self._has_column_filters(model_admin)

        # Decision: use custom class as-is or generate
        if base_class and not has_column_filters:
            # User provided complete FilterSet, use it directly
            return base_class

        if not has_column_filters:
            # No filters at all
            return None

        # Generate FilterSet from column configuration
        return self._generate_filterset_class(model, model_admin, base_class)

    def _generate_filterset_class(
        self, model: type[models.Model], model_admin, base_class: type[django_filters.FilterSet] | None = None
    ) -> type[django_filters.FilterSet]:
        """
        Generate a FilterSet class using factory pattern.

        Args:
            model: The Django model class
            model_admin: The ModelAdmin instance
            base_class: Optional base FilterSet class

        Returns:
            Generated FilterSet class
        """
        # Use default base if not provided
        if base_class is None:
            base_class = django_filters.FilterSet

        # Collect components
        filters = self._get_filters(model, model_admin, base_class)
        methods = self._get_filter_methods(model, model_admin, base_class)
        meta_class = self._build_meta_class(model, model_admin, base_class, filters)

        # Build class dict
        class_dict = {
            **filters,
            **methods,
            'Meta': meta_class,
        }

        # Generate class name
        class_name = f'{model.__name__}FilterSet'

        # Create the FilterSet class
        filterset_class = type(class_name, (base_class,), class_dict)

        return filterset_class

    def _get_filters(
        self, model: type[models.Model], model_admin, base_class: type[django_filters.FilterSet]
    ) -> dict[str, django_filters.Filter]:
        """
        Collect filter instances from column configuration.

        Args:
            model: The Django model class
            model_admin: The ModelAdmin instance
            base_class: The base FilterSet class

        Returns:
            Dictionary mapping field names to Filter instances
        """
        from djadmin.dataclasses import Column

        filters = {}

        for column in model_admin.list_display:
            # Only process Column objects with filter config
            if not isinstance(column, Column) or not column.filter:
                continue

            # Only handle string field names
            if not isinstance(column.field, str):
                continue

            field_name = column.field

            # Skip if already defined in base class
            if hasattr(base_class, field_name):
                continue

            # Get model field
            try:
                model_field = model._meta.get_field(field_name)
            except Exception:
                # Skip non-existent fields
                continue

            # Create filter instance
            filter_instance = self._create_filter(model_field, field_name, column.filter)

            if filter_instance:
                filters[field_name] = filter_instance

        return filters

    def _create_filter(self, model_field: models.Field, field_name: str, filter_config) -> django_filters.Filter | None:
        """
        Create a filter instance for a model field.

        Args:
            model_field: The Django model field
            field_name: The name of the field
            filter_config: The Filter dataclass instance

        Returns:
            A Filter instance, or None if unable to create
        """
        # Convert Filter dataclass to kwargs
        filter_kwargs = filter_config.to_kwargs()
        lookup_expr = filter_kwargs.get('lookup_expr', 'exact')

        # Handle explicit field_class (user override)
        if 'field_class' in filter_kwargs:
            filter_class = filter_kwargs.pop('field_class')
            # Note: method will be handled separately in _get_filter_methods
            return filter_class(**filter_kwargs)

        # Handle range filters (lookup_expr is a list)
        if isinstance(lookup_expr, list) and set(lookup_expr) == {'gte', 'lte'}:
            # Use RangeFilter for min/max
            filter_kwargs_copy = filter_kwargs.copy()
            filter_kwargs_copy.pop('lookup_expr')  # RangeFilter doesn't use this
            return django_filters.RangeFilter(**filter_kwargs_copy)

        # Use django-filter's built-in field-to-filter mapping
        filter_instance = django_filters.FilterSet.filter_for_field(
            model_field, field_name, lookup_expr=lookup_expr if isinstance(lookup_expr, str) else None
        )

        if not filter_instance:
            return None

        # Apply custom kwargs to the generated filter
        filter_class = type(filter_instance)
        merged_kwargs = {**filter_instance.extra, **filter_kwargs}

        return filter_class(**merged_kwargs)

    def _get_filter_methods(
        self, model: type[models.Model], model_admin, base_class: type[django_filters.FilterSet]
    ) -> dict[str, callable]:
        """
        Collect filter methods from column configuration.

        When a Filter has a callable method attribute, we bind it to the
        generated FilterSet class.

        Args:
            model: The Django model class
            model_admin: The ModelAdmin instance
            base_class: The base FilterSet class

        Returns:
            Dictionary mapping method names to callable methods
        """
        from djadmin.dataclasses import Column

        methods = {}

        for column in model_admin.list_display:
            if not isinstance(column, Column) or not column.filter:
                continue

            if not isinstance(column.field, str):
                continue

            field_name = column.field

            # Check if filter has a callable method
            method = getattr(column.filter, 'method', None)
            if method and callable(method):
                method_name = f'filter_{field_name}'
                methods[method_name] = method

        return methods

    def _build_meta_class(
        self,
        model: type[models.Model],
        model_admin,
        base_class: type[django_filters.FilterSet],
        new_filters: dict[str, django_filters.Filter],
    ) -> type:
        """
        Build the Meta class for the FilterSet.

        Args:
            model: The Django model class
            model_admin: The ModelAdmin instance
            base_class: The base FilterSet class
            new_filters: New filters being added

        Returns:
            Meta class
        """
        # Start with base class Meta attributes
        existing_meta = getattr(base_class, 'Meta', None)
        meta_attrs = {}

        if existing_meta:
            for attr in dir(existing_meta):
                if not attr.startswith('_'):
                    meta_attrs[attr] = getattr(existing_meta, attr)

        # Set model
        meta_attrs['model'] = model

        # Merge fields
        existing_fields = meta_attrs.get('fields', [])
        if existing_fields == '__all__':
            new_fields = '__all__'
        else:
            field_names = list(new_filters.keys())
            new_fields = list(set(list(existing_fields) + field_names))

        meta_attrs['fields'] = new_fields

        return type('Meta', (), meta_attrs)

    def _has_column_filters(self, model_admin) -> bool:
        """
        Check if ModelAdmin has any column-based filters.

        Note: Ordering is handled separately in the mixin, not via FilterSet.

        Args:
            model_admin: The ModelAdmin instance

        Returns:
            True if any columns have filter configuration
        """
        from djadmin.dataclasses import Column

        for column in model_admin.list_display:
            if isinstance(column, Column) and column.filter:
                return True

        return False
