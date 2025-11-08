"""
Utility functions for djadmin-formset plugin.

Provides helpers for working with django-formset FormCollections,
including test utilities for building POST data.
"""

from decimal import Decimal


def _convert_value_for_json(value):
    """Convert Python values to JSON-serializable format."""
    if isinstance(value, Decimal):
        return str(value)
    elif isinstance(value, list | tuple):
        return [_convert_value_for_json(v) for v in value]
    elif isinstance(value, dict):
        return {k: _convert_value_for_json(v) for k, v in value.items()}
    return value


def build_create_post_data(action, **field_values):
    """
    Build hierarchical POST data for testing CREATE operations.

    Uses django-formset's model_to_dict() to get the proper hierarchical structure
    from an unsaved model instance, then updates with the provided field values.

    Args:
        action: The Action instance (e.g., AddAction) with get_view_class() method
        **field_values: Field values to include in the POST data

    Returns:
        dict: Hierarchical data dict ready for JSON POST

    Example:
        >>> from djadmin import site
        >>> from examples.webshop.models import Product
        >>> product_admin = site.get_model_admins(Product)[0]
        >>> add_action = [a for a in product_admin.general_actions if a.__class__.__name__ == 'AddAction'][0]
        >>> post_data = build_create_post_data(
        ...     add_action,
        ...     name='New Product',
        ...     price='99.99',
        ...     category=category.id
        ... )
        >>> response = client.post(url, data=post_data, content_type='application/json')
    """
    # Get view class from action
    view_class = action.get_view_class()

    # Instantiate view with minimal required attributes
    view = view_class()
    view.model = action.model
    view.model_admin = action.model_admin
    view.action = action

    # Get the FormCollection class the same way the view does
    form_collection_class = view.get_collection_class()

    # Create an unsaved instance and use django-formset's model_to_dict()
    # This gives us the correct hierarchical structure with default values
    empty_instance = action.model()
    form_collection = form_collection_class()
    hierarchical_data = form_collection.model_to_dict(empty_instance)

    # Update fields with provided values
    def update_fields(data_dict, field_updates):
        """Recursively update field values in hierarchical structure."""
        for key, value in data_dict.items():
            if isinstance(value, dict):
                # Check if this is a single-field form: {field_name: {field_name: value}}
                if len(value) == 1 and list(value.keys())[0] == key:
                    # Update this field if it's in field_updates
                    if key in field_updates:
                        data_dict[key] = {key: field_updates[key]}
                elif 'main' in value and isinstance(value['main'], dict):
                    # This is a row form: {row_name: {'main': {field1: val1, ...}}}
                    for field_name in value['main'].keys():
                        if field_name in field_updates:
                            value['main'][field_name] = field_updates[field_name]
                else:
                    # Check if this is a flat form (no layout): {form: {field1: val1, field2: val2}}
                    # In this case, all keys in value are field names
                    is_flat_form = all(
                        not isinstance(v, dict) or (isinstance(v, dict) and not v) or isinstance(v, list)
                        for v in value.values()
                    )
                    if is_flat_form:
                        # Flat form - update fields directly
                        for field_name in list(value.keys()):
                            if field_name in field_updates:
                                value[field_name] = field_updates[field_name]
                    else:
                        # Recurse into nested structures (fieldsets)
                        update_fields(value, field_updates)
            elif isinstance(value, list):
                # This is a Collection - replace if provided
                if key in field_updates:
                    data_dict[key] = field_updates[key]

    update_fields(hierarchical_data, field_values)

    # Convert Decimal and other non-JSON-serializable values
    hierarchical_data = _convert_value_for_json(hierarchical_data)

    # Wrap in formset_data key as expected by FormCollectionViewMixin
    return {'formset_data': hierarchical_data}


def build_update_post_data(action, instance, **field_updates):
    """
    Build hierarchical POST data for testing UPDATE operations.

    Uses django-formset's model_to_dict() to get the proper hierarchical structure
    from the existing instance, then updates with the provided field values.

    Args:
        action: The Action instance (e.g., EditRecordAction) with get_view_class() method
        instance: The model instance being updated
        **field_updates: Field values to update/override

    Returns:
        dict: Hierarchical data dict ready for JSON POST

    Example:
        >>> from djadmin import site
        >>> from examples.webshop.models import Product
        >>> product_admin = site.get_model_admins(Product)[0]
        >>> edit_action = [a for a in product_admin.record_actions if a.__class__.__name__ == 'EditAction'][0]
        >>> post_data = build_update_post_data(
        ...     edit_action,
        ...     instance=product,
        ...     price='149.99'  # Update just the price
        ... )
        >>> response = client.post(url, data=post_data, content_type='application/json')
    """
    # Get view class from action
    view_class = action.get_view_class()

    # Instantiate view with minimal required attributes
    view = view_class()
    view.model = action.model
    view.model_admin = action.model_admin
    view.action = action

    # Get the FormCollection class the same way the view does
    form_collection_class = view.get_collection_class()

    # Use model_to_dict to get hierarchical data from instance
    form_collection = form_collection_class()
    hierarchical_data = form_collection.model_to_dict(instance)

    # Update fields with provided values
    def update_fields(data_dict, field_updates):
        """Recursively update field values in hierarchical structure."""
        for key, value in data_dict.items():
            if isinstance(value, dict):
                # Check if this is a single-field form: {field_name: {field_name: value}}
                if len(value) == 1 and list(value.keys())[0] == key:
                    # Update this field if it's in field_updates
                    if key in field_updates:
                        data_dict[key] = {key: field_updates[key]}
                elif 'main' in value and isinstance(value['main'], dict):
                    # This is a row form: {row_name: {'main': {field1: val1, ...}}}
                    for field_name in value['main'].keys():
                        if field_name in field_updates:
                            value['main'][field_name] = field_updates[field_name]
                else:
                    # Check if this is a flat form (no layout): {form: {field1: val1, field2: val2}}
                    # In this case, all keys in value are field names
                    is_flat_form = all(
                        not isinstance(v, dict) or (isinstance(v, dict) and not v) or isinstance(v, list)
                        for v in value.values()
                    )
                    if is_flat_form:
                        # Flat form - update fields directly
                        for field_name in list(value.keys()):
                            if field_name in field_updates:
                                value[field_name] = field_updates[field_name]
                    else:
                        # Recurse into nested structures (fieldsets)
                        update_fields(value, field_updates)
            elif isinstance(value, list):
                # This is a Collection - replace if provided
                if key in field_updates:
                    data_dict[key] = field_updates[key]

    update_fields(hierarchical_data, field_updates)

    # Convert Decimal and other non-JSON-serializable values
    hierarchical_data = _convert_value_for_json(hierarchical_data)

    # Wrap in formset_data key as expected by FormCollectionViewMixin
    return {'formset_data': hierarchical_data}
