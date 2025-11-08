"""
Plugin hooks for djadmin-formset.

Implements djadmin hooks to provide django-formset FormCollection integration.
"""

from pluggy import HookimplMarker

hookimpl = HookimplMarker('djadmin')


@hookimpl
def djadmin_provides_features():
    """
    Advertise features provided by this plugin.

    CRITICAL: This hook allows the core feature validation system to check
    that all requested features are available at Django startup.

    Returns:
        List of feature names this plugin provides:
        - collections/inlines: Inline editing via Collection components
        - conditional_fields: show_if/hide_if field visibility
        - computed_fields: calculate attribute for computed values
    """
    return [
        'collections',
        'inlines',  # Alias for collections
        'conditional_fields',
        'computed_fields',
    ]


@hookimpl
def djadmin_get_required_apps():
    """
    Declare required apps for djadmin-formset plugin.

    This plugin requires django-formset (the 'formset' app) to be installed.
    We use Before() to ensure templates are discovered before core djadmin templates.

    CRITICAL: djadmin_formset must load BEFORE djadmin to override templates.
    Django's template loader uses first-match resolution, so our templates in
    djadmin_formset/templates/djadmin/actions/edit.html must be found before
    djadmin/templates/djadmin/actions/edit.html.

    Returns:
        List of required apps with ordering modifiers.
    """
    from djadmin.plugins.modifiers import Before

    return [
        Before('formset'),  # django-formset needs early loading
        Before('djadmin_formset'),  # Our plugin app - MUST be before djadmin for template overrides
    ]


@hookimpl
def djadmin_get_action_view_mixins(action):
    """
    Provide view mixins for form-based actions.

    This hook injects the appropriate DjAdminFormset mixin for each action type:
    - CreateViewActionMixin: DjAdminFormsetCreateMixin (sets self.object = None)
    - UpdateViewActionMixin: DjAdminFormsetUpdateMixin (uses EditCollectionView as-is)
    - FormViewActionMixin: Base mixin + FormCollectionViewMixin

    The mixins provide get_collection_class() which converts djadmin layouts
    to django-formset FormCollections.

    Args:
        action: The action instance (not used, but required by hook spec)

    Returns:
        Dict mapping action base classes to lists of mixins
    """
    from djadmin.actions.view_mixins import CreateViewActionMixin, FormViewActionMixin, UpdateViewActionMixin
    from formset.views import FormCollectionViewMixin

    from djadmin_formset.mixins import (
        DjAdminFormsetBaseMixin,
        DjAdminFormsetCreateMixin,
        DjAdminFormsetUpdateMixin,
    )

    return {
        FormViewActionMixin: [FormCollectionViewMixin, DjAdminFormsetBaseMixin],
        CreateViewActionMixin: [DjAdminFormsetCreateMixin],
        UpdateViewActionMixin: [DjAdminFormsetUpdateMixin],
    }


@hookimpl
def djadmin_get_action_view_assets(action):
    """
    Provide django-formset JS assets for form-based actions.

    This hook registers the required django-formset JavaScript for all
    form-based action views (AddAction, EditRecordAction, etc.).

    Note: We don't include formset's bootstrap5-extra.css since we're using
    Tailwind/custom CSS. Custom styling for FormCollections will be handled
    separately.

    Args:
        action: The action instance (not used, but required by hook spec)

    Returns:
        Dict mapping action base classes to asset dicts with JSAsset list
    """
    from djadmin import JSAsset
    from djadmin.actions.view_mixins import CreateViewActionMixin, FormViewActionMixin, UpdateViewActionMixin

    # Same assets for all form-based views
    # Note: ES modules are always deferred by spec. FOUC prevention is handled via CSS (:not(:defined))
    formset_assets = {
        'js': [
            JSAsset(src='formset/js/django-formset.js', module=True),
        ],
    }

    return {
        FormViewActionMixin: formset_assets,
        CreateViewActionMixin: formset_assets,
        UpdateViewActionMixin: formset_assets,
    }


@hookimpl
def djadmin_get_action_view_base_class(action):
    """
    Provide view base classes for create and update actions.

    This hook sets django-formset's EditCollectionView as the base for both
    CREATE and UPDATE actions. EditCollectionView has the form_collection_valid()
    implementation that saves data via construct_instance().

    For CREATE actions, self.object will be None (set by our mixin).
    For UPDATE actions, self.object is set by SingleObjectMixin.get_object().

    Args:
        action: The action instance (not used, but required by hook spec)

    Returns:
        Dict mapping action base classes to view base class
    """
    from djadmin.actions.view_mixins import CreateViewActionMixin, UpdateViewActionMixin
    from formset.views import EditCollectionView

    return {
        CreateViewActionMixin: EditCollectionView,
        UpdateViewActionMixin: EditCollectionView,
    }


@hookimpl
def djadmin_get_test_methods():
    """
    Provide FormCollection-aware test methods that override core plugin tests.

    These test methods handle the hierarchical JSON POST data format required
    by django-formset's FormCollection instead of standard Django form data.

    Uses Replace() modifier to explicitly override the core plugin's POST test methods.

    Returns:
        Dict mapping action base classes to test method callables using Replace() modifiers.
    """
    from djadmin.actions.view_mixins import CreateViewActionMixin, UpdateViewActionMixin
    from djadmin.plugins.modifiers import Replace

    from djadmin_formset.utils import build_create_post_data, build_update_post_data

    def test_formset_create_post(test_case, action):
        """Test POST request to create view with FormCollection data."""
        url = test_case._get_action_url(action)

        # Get field data from test case
        create_data = test_case.get_create_data()

        # Build hierarchical JSON structure for FormCollection
        # Pass action directly (has get_view_class() method for proper layout resolution)
        post_data = build_create_post_data(action, **create_data)

        # Count before create
        count_before = test_case.model.objects.count()

        # POST with JSON content type
        response = test_case.client.post(url, data=post_data, content_type='application/json')

        # Should redirect or show success (200 if form re-rendered with success)
        if response.status_code not in [200, 302]:
            # Debug output for validation errors
            import json

            try:
                error_data = json.loads(response.content)
                action_name = action.__class__.__name__
                errors_json = json.dumps(error_data, indent=2)
                error_msg = f'Create POST failed for {action_name}: {response.status_code}\nErrors: {errors_json}'
            except Exception:
                action_name = action.__class__.__name__
                response_text = response.content.decode()[:500]
                error_msg = f'Create POST failed for {action_name}: {response.status_code}\nResponse: {response_text}'
            test_case.fail(error_msg)

        test_case.assertIn(
            response.status_code,
            [200, 302],
            f'Create POST failed for {action.__class__.__name__}: {response.status_code}',
        )

        # Object should be created
        test_case.assertEqual(
            test_case.model.objects.count(),
            count_before + 1,
            f'Object not created for {action.__class__.__name__}',
        )

        # Custom assertions
        test_case.assert_create_successful(response, create_data)

    def test_formset_update_get(test_case, action):
        """Test GET request to update view with FormCollection."""
        url = test_case._get_action_url(action, test_case.obj)
        response = test_case.client.get(url)

        test_case.assertEqual(response.status_code, 200, f'Update GET failed for {action.__class__.__name__}')

        # FormCollection view should have form_collection in context, not form
        test_case.assertIn(
            'form_collection', response.context, f'No form_collection in context for {action.__class__.__name__}'
        )

        # EditCollectionView provides 'object' in context (from SingleObjectMixin)
        test_case.assertIn('object', response.context, f'No object in context for {action.__class__.__name__}')
        test_case.assertEqual(
            response.context['object'].pk,
            test_case.obj.pk,
            f'Context object not correct for {action.__class__.__name__}',
        )

    def test_formset_update_post(test_case, action):
        """Test POST request to update view with FormCollection data."""
        url = test_case._get_action_url(action, test_case.obj)

        # Build hierarchical JSON structure for FormCollection
        # Pass action directly (has get_view_class() method for proper layout resolution)
        # Pass instance and field updates separately
        post_data = build_update_post_data(action, test_case.obj, **test_case.to_update_fields)

        # POST with JSON content type
        response = test_case.client.post(url, data=post_data, content_type='application/json')

        # Should redirect or show success
        test_case.assertIn(
            response.status_code,
            [200, 302],
            f'Update POST failed for {action.__class__.__name__}: {response.status_code}',
        )

        # Object should be updated
        test_case.obj.refresh_from_db()
        for field, value in test_case.to_update_fields.items():
            test_case.assertEqual(
                getattr(test_case.obj, field),
                value,
                f'Field {field} not updated for {action.__class__.__name__}',
            )

        # Custom assertions
        test_case.assert_update_successful(response, test_case.obj, post_data)

    # Use Replace() modifier to explicitly override the core plugin's test methods for FormCollection
    return {
        CreateViewActionMixin: {
            '_test_create_post': Replace(CreateViewActionMixin, '_test_create_post', test_formset_create_post),
        },
        UpdateViewActionMixin: {
            '_test_update_get': Replace(UpdateViewActionMixin, '_test_update_get', test_formset_update_get),
            '_test_update_post': Replace(UpdateViewActionMixin, '_test_update_post', test_formset_update_post),
        },
    }
