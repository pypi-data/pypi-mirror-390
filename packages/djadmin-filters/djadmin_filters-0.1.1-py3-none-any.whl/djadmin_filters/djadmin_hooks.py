"""Plugin hooks for djadmin integration."""

from djadmin.plugins import hookimpl


@hookimpl
def djadmin_provides_features():
    """Advertise features provided by this plugin."""
    return ['filter', 'ordering', 'search']


@hookimpl
def djadmin_get_required_apps():
    """
    Declare required apps for djadmin-filters plugin.

    This plugin requires django-filter (the 'django_filters' app) to be installed.

    Returns:
        List of required apps (no special ordering needed).
    """
    return [
        'django_filters',  # django-filter package
        'djadmin_filters',  # Our plugin app
    ]


@hookimpl
def djadmin_get_action_view_mixins(action):
    """
    Provide mixins for ListView actions.

    This will add filtering, ordering, and search capabilities to ListView.
    """
    from djadmin.plugins.core.actions import ListAction

    from .mixins import DjAdminFiltersMixin

    return {ListAction: [DjAdminFiltersMixin]}


@hookimpl
def djadmin_get_action_view_assets(action):
    """
    Provide CSS and JS assets for ListView actions.

    This adds the plugin's stylesheet and JavaScript for UI enhancements.
    """
    from djadmin.plugins.core.actions import ListAction

    return {
        ListAction: {
            'css': ['djadmin/djadmin_filters/css/djadmin_filters.css'],
            'js': ['djadmin/djadmin_filters/js/djadmin_filters.js'],
        }
    }


@hookimpl
def djadmin_get_sidebar_widgets(action):
    """
    Provide sidebar widgets for ListView actions.

    This adds a filter widget to the sidebar when filters are configured.
    """
    from djadmin.dataclasses import SidebarWidget
    from djadmin.plugins.core.actions import ListAction

    def should_display_filters(view, request):
        """Only display if filterset exists on the view."""
        return hasattr(view, 'filterset') and view.filterset is not None

    def get_filter_context(view, request):
        """Provide filterset and filter state to template."""
        context = {'filterset': getattr(view, 'filterset', None)}

        # Add has_active_filters and clear_filters_url from the view's context
        # These are set by DjAdminFiltersMixin.get_context_data()
        if hasattr(view, 'filterset') and view.filterset is not None:
            # Call the mixin's helper methods to get the values
            if hasattr(view, '_has_active_filters'):
                context['has_active_filters'] = view._has_active_filters()
            if hasattr(view, '_get_clear_filters_url'):
                context['clear_filters_url'] = view._get_clear_filters_url()

        return context

    return {
        ListAction: [
            SidebarWidget(
                template='djadmin/djadmin_filters/filter_widget.html',
                context_callback=get_filter_context,
                condition=should_display_filters,
                order=10,  # Show filters first in sidebar
                identifier='filters',
            )
        ]
    }


def get_sort_icon_template(column, request):
    """Determine which sort icon to show based on current ordering."""
    current_ordering = request.GET.get('ordering', '')
    field_name = column.field if isinstance(column.field, str) else None

    if not field_name:
        return 'djadmin/icons/sort.html'

    if current_ordering == field_name:
        return 'djadmin/icons/sort-up.html'
    elif current_ordering == f'-{field_name}':
        return 'djadmin/icons/sort-down.html'
    return 'djadmin/icons/sort.html'


def get_sort_url(column, request):
    """Generate URL for sorting by this column."""
    from urllib.parse import urlencode

    field_name = column.field if isinstance(column.field, str) else None
    if not field_name:
        return None

    current_ordering = request.GET.get('ordering', '')

    # Determine sort state: 0 = neutral, 1 = asc, -1 = desc
    if current_ordering == field_name:
        sort_state = 1  # Currently ascending
    elif current_ordering == f'-{field_name}':
        sort_state = -1  # Currently descending
    else:
        sort_state = 0  # Not sorted (neutral)

    # Toggle: neutral → asc, then toggle between asc ↔ desc
    new_sort_state = 1 if sort_state == 0 else -sort_state
    new_ordering = f'-{field_name}' if new_sort_state == -1 else field_name

    # Build URL with ordering parameter (preserve other query params)
    params = request.GET.copy()
    params['ordering'] = new_ordering

    query_string = urlencode(params)
    return f'?{query_string}' if query_string else '?'


def get_sort_title(column, request):
    """Generate tooltip text based on current sort state."""
    field_name = column.field if isinstance(column.field, str) else None
    if not field_name:
        return ''

    current_ordering = request.GET.get('ordering', '')
    column_label = column.label or field_name.replace('_', ' ').title()

    if current_ordering == field_name:
        return f'Sorted by {column_label} (ascending). Click to sort descending.'
    elif current_ordering == f'-{field_name}':
        return f'Sorted by {column_label} (descending). Click to sort ascending.'
    return f'Click to sort by {column_label} (ascending)'


def should_display_sort_icon(column, request):
    """Only show sort icon for columns with order configuration."""
    return bool(column.order)


@hookimpl
def djadmin_get_column_header_icons(action):
    """
    Provide column header icons for sortable columns.

    This adds sort indicators to column headers when ordering is enabled.
    """
    from djadmin.dataclasses import ColumnHeaderIcon
    from djadmin.plugins.core.actions import ListAction

    return {
        ListAction: [
            ColumnHeaderIcon(
                icon_template=get_sort_icon_template,
                url=get_sort_url,
                title=get_sort_title,
                condition=should_display_sort_icon,
                order=10,
                identifier='sort',
            )
        ]
    }
