"""Django app configuration for djadmin-formset plugin."""

from django.apps import AppConfig


class DjAdminFormsetConfig(AppConfig):
    """
    Django app configuration for djadmin-formset plugin.

    This plugin provides django-formset FormCollection integration for
    django-admin-deux Layout API, enabling:
    - Inline editing (Collections)
    - Conditional fields (show_if/hide_if)
    - Computed fields (calculate)
    - Client-side validation
    - Drag-and-drop ordering
    """

    name = 'djadmin_formset'
    verbose_name = 'Django Admin Deux - Formset Integration'
    default_auto_field = 'django.db.models.BigAutoField'
