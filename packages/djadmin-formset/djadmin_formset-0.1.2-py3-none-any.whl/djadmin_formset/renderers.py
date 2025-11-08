"""
Custom renderers for django-formset integration.

This module provides the DjAdminFormRenderer class that customizes
django-formset rendering for the djadmin theme.
"""

from django.conf import settings
from formset.renderers.default import FormRenderer


class DjAdminFormRenderer(FormRenderer):
    """
    Custom FormRenderer for django-admin-deux theme.

    This renderer customizes django-formset rendering to match the djadmin
    Tailwind-based theme. It provides appropriate CSS classes and template
    paths for seamless integration.

    CSS Classes:
        - field_css_classes: Applied to field wrappers
        - label_css_classes: Applied to field labels
        - control_css_classes: Applied to form controls (inputs, selects, etc.)
        - form_css_classes: Applied to form elements
        - fieldset_css_classes: Applied to fieldset elements
        - collection_css_classes: Applied to collection wrappers

    Template Customization:
        Templates can be overridden via the DJADMIN_FORMSET_TEMPLATES setting:

        DJADMIN_FORMSET_TEMPLATES = {
            'form': 'myapp/custom_form.html',
            'fieldset': 'myapp/custom_fieldset.html',
            'collection': 'myapp/custom_collection.html',
        }

    Usage:
        # In ModelAdmin
        from djadmin import ModelAdmin, Layout, Field
        from djadmin_formset.renderers import DjAdminFormRenderer

        class MyModelAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('email'),
                renderer=DjAdminFormRenderer,  # Use custom renderer
            )

        # Or use default (DjAdminFormRenderer is used automatically)
        class MyModelAdmin(ModelAdmin):
            layout = Layout(
                Field('name'),
                Field('email'),
            )
    """

    def __init__(self, **kwargs):
        """
        Initialize the DjAdminFormRenderer with djadmin theme CSS classes.

        All CSS classes can be overridden by passing keyword arguments.

        Keyword Args:
            field_css_classes (str|list): CSS classes for field wrappers
            label_css_classes (str|list): CSS classes for labels
            control_css_classes (str|list): CSS classes for form controls
            form_css_classes (str|list): CSS classes for forms
            fieldset_css_classes (str|list): CSS classes for fieldsets
            collection_css_classes (str|list): CSS classes for collections
            max_options_per_line (int): Max number of radio/checkbox options per line
            exempt_feedback (bool): Whether to exempt feedback messages
        """
        # No CSS classes - use semantic HTML-based styling in CSS
        defaults = {
            'field_css_classes': None,
            'label_css_classes': None,
            'control_css_classes': None,
            'form_css_classes': None,
            'fieldset_css_classes': None,
            'collection_css_classes': None,
        }

        # Merge defaults with any provided kwargs
        for key, value in defaults.items():
            kwargs.setdefault(key, value)

        super().__init__(**kwargs)

    def _amend_fieldset(self, context):
        """
        Amend the context for fieldset rendering.

        This method customizes the fieldset rendering context to:
        1. Apply djadmin CSS classes
        2. Set the help text template
        3. Support unnamed fieldsets (legend=None)

        Args:
            context (dict): The rendering context

        Returns:
            dict: The amended context
        """
        # Call parent implementation
        context = super()._amend_fieldset(context)

        # Get template override from settings if available
        template_overrides = getattr(settings, 'DJADMIN_FORMSET_TEMPLATES', {})

        # Override help text template if configured
        if 'help_text' in template_overrides:
            context['help_text_template'] = template_overrides['help_text']
        else:
            # Use formset default
            context['help_text_template'] = 'formset/default/help_text.html'

        # The fieldset template already handles legend=None correctly
        # (it only renders <legend> if legend is truthy)
        # No additional customization needed for unnamed fieldsets

        return context

    def _amend_form(self, context):
        """
        Amend the context for form rendering.

        This method allows template overrides via settings.

        Args:
            context (dict): The rendering context

        Returns:
            dict: The amended context
        """
        context = super()._amend_form(context)

        # Template overrides are handled by FormRenderer base class
        # We just need to provide our CSS classes (already done in __init__)
        # Settings can be accessed via: getattr(settings, 'DJADMIN_FORMSET_TEMPLATES', {})

        return context

    def _amend_collection(self, context):
        """
        Amend the context for collection rendering.

        This method customizes collection rendering for djadmin theme.

        Args:
            context (dict): The rendering context

        Returns:
            dict: The amended context
        """
        context = super()._amend_collection(context)

        # Collections use the CSS classes set in __init__
        # No additional customization needed

        return context


class HorizontalFormRenderer(FormRenderer):
    """
    Renderer for Row components - displays fields horizontally using flexbox.

    This renderer is used by Row FormCollections to render fields side-by-side
    instead of stacked vertically. It applies flexbox CSS classes to create
    a horizontal layout while maintaining the djadmin theme.

    CSS Classes:
        - form_css_classes: 'flex gap-4 mb-4' (flexbox container)
        - field_css_classes: 'flex-1 px-2' (flex items with padding)
        - All other classes match DjAdminFormRenderer

    Usage:
        # Automatically used by FormFactory for Row components
        row = Row(
            Field('first_name'),
            Field('last_name'),
        )

        # Or set explicitly
        layout = Layout(
            Row(...),
            renderer=HorizontalFormRenderer,
        )
    """

    def __init__(self, **kwargs):
        """
        Initialize the HorizontalFormRenderer with flexbox CSS classes.

        All CSS classes can be overridden by passing keyword arguments.

        Keyword Args:
            field_css_classes (str|list): CSS classes for field wrappers (default: 'flex-1 px-2')
            form_css_classes (str|list): CSS classes for forms (default: 'flex gap-4 mb-4')
            label_css_classes (str|list): CSS classes for labels
            control_css_classes (str|list): CSS classes for form controls
            fieldset_css_classes (str|list): CSS classes for fieldsets
            collection_css_classes (str|list): CSS classes for collections
        """
        # Only apply 'row' marker class - all styling done in CSS
        defaults = {
            'field_css_classes': None,
            'label_css_classes': None,
            'control_css_classes': None,
            'form_css_classes': None,
            'fieldset_css_classes': None,
            'collection_css_classes': 'row',  # Marker class for Row FormCollections
        }

        # Merge defaults with any provided kwargs
        for key, value in defaults.items():
            kwargs.setdefault(key, value)

        super().__init__(**kwargs)


def get_default_renderer():
    """
    Get the default renderer class.

    This function returns the DjAdminFormRenderer class as the default
    renderer for djadmin-formset. It can be used by the FormFactory to
    set the default renderer.

    Returns:
        Type[DjAdminFormRenderer]: The default renderer class
    """
    return DjAdminFormRenderer
