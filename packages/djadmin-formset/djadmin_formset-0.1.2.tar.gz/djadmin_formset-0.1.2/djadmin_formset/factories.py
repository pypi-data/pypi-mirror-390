"""
FormFactory for converting Layout API to django-formset FormCollections.

This module provides the core functionality for transforming djadmin Layout objects
into django-formset FormCollection classes, enabling inline editing, conditional
fields, computed fields, and client-side validation.
"""

from djadmin.layout import Collection, Field, Fieldset, Layout, Row
from django.db import models
from django.forms import ModelForm
from formset.collection import FormCollection


def ensure_formset_mixin(form_class):
    """
    Ensure a form class has FormMixin.

    If the form class doesn't already have the mixin, create a new class
    that extends both FormMixin and the original form class.

    Args:
        form_class: The form class to check/wrap

    Returns:
        Form class with FormMixin

    Example:
        UserCreationForm -> UserCreationFormWithFormMixin(FormMixin, UserCreationForm)
    """
    from formset.forms import FormMixin

    # Check if already has FormMixin
    if issubclass(form_class, FormMixin):
        return form_class

    # Create new class with FormMixin
    return type(
        f'{form_class.__name__}Set',
        (FormMixin, form_class),
        {},
    )


class FormFactory:
    """
    Factory for building django-formset FormCollection classes from Layout definitions.

    The FormFactory processes Layout objects and generates FormCollection classes that
    support all advanced features:
    - Inline editing (Collection components)
    - Conditional fields (show_if/hide_if)
    - Computed fields (calculate)
    - Client-side validation
    - Drag-and-drop ordering (is_sortable)

    Example:
        layout = Layout(
            Field('name'),
            Collection('books',
                model=Book,
                fields=['title', 'isbn'],
                is_sortable=True,
            ),
        )

        form_collection_class = FormFactory.from_layout(
            layout=layout,
            model=Author,
            base_form=AuthorForm,
        )
    """

    @staticmethod
    def from_layout(
        layout: Layout,
        model: type[models.Model],
        base_form: type[ModelForm] | None = None,
        renderer: type | None = None,
    ) -> type[FormCollection]:
        """
        Build a FormCollection class from a Layout definition using hierarchical structure.

        This is the main entry point for converting a djadmin Layout into a
        django-formset FormCollection. Uses method dispatch pattern to process
        each layout item, creating a hierarchical FormCollection structure that
        preserves Fieldset and Row organization.

        Architecture:
            - Each Fieldset → FormCollection (with legend)
            - Each Row → FormCollection (with HorizontalFormRenderer)
            - Each Collection → FormCollection (nested, for related objects)
            - Each Field → Single-field Form (terminal element)

        This allows the renderer to properly handle Fieldsets with legends
        and Rows with horizontal layout, while also supporting inline editing
        via Collections.

        Args:
            layout: The Layout object to convert
            model: The Django model class
            base_form: Optional base ModelForm class (defaults to ModelForm)
            renderer: Optional custom renderer (will be set as default_renderer)

        Returns:
            A FormCollection class ready to be instantiated

        Example:
            form_class = FormFactory.from_layout(
                layout=author_admin.layout,
                model=Author,
                base_form=AuthorForm,
            )
            form = form_class()

        Structure:
            The generated FormCollection will have hierarchical structure:
            - <fieldset_name>: FormCollection for each Fieldset
            - <row_name>: FormCollection for each Row
            - <collection_name>: FormCollection for each Collection
            - <field_name>: Form for each standalone Field
        """
        from djadmin_formset.renderers import DjAdminFormRenderer

        # Use DjAdminFormRenderer by default
        renderer = renderer or DjAdminFormRenderer

        # Build collection attributes
        collection_attrs = {
            '_layout': layout,
            'default_renderer': renderer,
        }

        # Process each layout item via method dispatch
        for idx, item in enumerate(layout.items):
            FormFactory._process_layout_item(
                item=item,
                collection_attrs=collection_attrs,
                model=model,
                base_form=base_form,
                item_index=idx,
            )

        # Create and return top-level FormCollection class
        collection_class = type(
            f'{model.__name__}FormCollection',
            (FormCollection,),
            collection_attrs,
        )

        return collection_class

    @staticmethod
    def wrap_form_in_collection(
        form_class: type[ModelForm],
        model: type[models.Model],
        renderer: type | None = None,
    ) -> type[FormCollection]:
        """
        Wrap a single form class in a FormCollection.

        Used when form_class is provided but no layout exists.
        Creates a simple FormCollection with a single form holder.

        CRITICAL: Ensures form_class has FormsetMixin before wrapping.

        Args:
            form_class: The form class to wrap
            model: The Django model class
            renderer: Optional custom renderer

        Returns:
            A FormCollection class with the form as its only member

        Example:
            collection_class = FormFactory.wrap_form_in_collection(
                form_class=UserPasswordChangeForm,
                model=User,
                renderer=DjAdminFormRenderer,
            )
            collection = collection_class(instance=user)
        """
        from djadmin_formset.renderers import DjAdminFormRenderer

        renderer = renderer or DjAdminFormRenderer

        # Ensure form class has FormsetMixin
        form_class_with_mixin = ensure_formset_mixin(form_class)

        # Create FormCollection with single form holder
        collection_attrs = {
            'default_renderer': renderer,
            'form': form_class_with_mixin(),  # Single form instance with mixin
        }

        collection_class = type(
            f'{model.__name__}FormCollection',
            (FormCollection,),
            collection_attrs,
        )

        return collection_class

    @staticmethod
    def _process_layout_item(
        item,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Dispatch to item-specific handler using method dispatch pattern.

        This method uses getattr() to dynamically find the appropriate handler
        method based on the item type. NO if/elif chains - follows the method
        dispatch pattern from CLAUDE.md.

        Handler methods are named `_process_{item_type}` where item_type is
        the lowercase class name (e.g., 'field', 'fieldset', 'row', 'collection').

        Args:
            item: The layout item to process (Field, Fieldset, Row, or Collection)
            collection_attrs: Dictionary to add processed items to
            model: The Django model class
            base_form: Optional base ModelForm class
            item_index: Index of this item in the parent's items list

        Raises:
            ValueError: If the item type is not supported (via _process_unsupported)

        Example:
            # Dispatches to _process_field()
            FormFactory._process_layout_item(
                item=Field('name'),
                collection_attrs={},
                model=Customer,
                base_form=None,
                item_index=0,
            )
        """
        item_type = type(item).__name__.lower()
        handler = getattr(
            FormFactory,
            f'_process_{item_type}',
            FormFactory._process_unsupported,
        )
        return handler(
            item=item,
            collection_attrs=collection_attrs,
            model=model,
            base_form=base_form,
            item_index=item_index,
        )

    @staticmethod
    def _process_unsupported(
        item,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Handle unknown layout item types.

        Called by _process_layout_item() when no specific handler is found.

        Args:
            item: The unsupported layout item
            collection_attrs: Dictionary to add processed items to
            model: The Django model class
            base_form: Optional base ModelForm class
            item_index: Index of this item in the parent's items list

        Raises:
            ValueError: Always raised with descriptive error message
        """
        raise ValueError(
            f'Unsupported layout item type: {type(item).__name__}. '
            f'Supported types: Field, Fieldset, Row, Collection'
        )

    @staticmethod
    def _is_field_non_editable(field_name: str, model: type[models.Model]) -> bool:
        """
        Check if a model field is non-editable.

        Non-editable fields (editable=False) cannot be included in ModelForm's
        Meta.fields. Instead, they must be included in Meta.disabled_fields
        (django-formset feature) to display them as readonly.

        Args:
            field_name: The field name to check
            model: The Django model class

        Returns:
            bool: True if field has editable=False, False otherwise

        Example:
            >>> FormFactory._is_field_non_editable('order_number', Order)
            True  # If order_number has editable=False
        """
        try:
            model_field = model._meta.get_field(field_name)
            return not model_field.editable
        except Exception:
            return False

    @staticmethod
    def _is_model_field(field_name: str, model: type[models.Model]) -> bool:
        """
        Check if a field name corresponds to a model field.

        Returns True if the field exists on the model and is a Django field.
        Returns False for form-only fields (like password1, password2).

        This is critical for forms with non-model fields (e.g., UserCreationForm
        with password1/password2 fields). These fields should NOT be included in
        Meta.fields because they don't exist on the model - they're defined
        directly on the form class.

        Args:
            field_name: Name of the field to check
            model: The Django model class

        Returns:
            bool: True if field is a model field, False otherwise

        Example:
            >>> FormFactory._is_model_field('username', User)
            True
            >>> FormFactory._is_model_field('password1', User)  # Form-only field
            False
        """
        from django.core.exceptions import FieldDoesNotExist

        try:
            field = model._meta.get_field(field_name)
            return isinstance(field, models.Field)
        except FieldDoesNotExist:
            return False

    @staticmethod
    def _apply_field_config(form_fields: dict, field_def: Field):
        """
        Apply Field configuration to a form field.

        Applies all customizations from a Field definition to the corresponding
        Django form field, including:
        - label, widget, required, help_text, initial
        - django-formset features (df-show, df-hide, df-calculate)
        - custom attrs and extra_kwargs

        Args:
            form_fields: Dictionary of form fields (from form.fields)
            field_def: The Field definition from the layout

        Example:
            field_def = Field('name', label='Full Name', required=True)
            FormFactory._apply_field_config(form.fields, field_def)
            # Now form.fields['name'].label == 'Full Name'
        """
        if field_def.name not in form_fields:
            return

        form_field = form_fields[field_def.name]

        # Apply basic configurations
        if field_def.label is not None:
            form_field.label = field_def.label

        if field_def.widget is not None:
            if isinstance(field_def.widget, type):
                form_field.widget = field_def.widget()
            else:
                form_field.widget = field_def.widget

        if field_def.required is not None:
            form_field.required = field_def.required

        if field_def.help_text is not None:
            form_field.help_text = field_def.help_text

        if field_def.initial is not None:
            form_field.initial = field_def.initial

        # Apply django-formset features
        if field_def.show_if:
            form_field.widget.attrs['df-show'] = field_def.show_if

        if field_def.hide_if:
            form_field.widget.attrs['df-hide'] = field_def.hide_if

        if field_def.calculate:
            form_field.widget.attrs['df-calculate'] = field_def.calculate

        # Apply custom attrs
        if field_def.attrs:
            form_field.widget.attrs.update(field_def.attrs)

        # Apply extra_kwargs
        for key, value in field_def.extra_kwargs.items():
            setattr(form_field, key, value)

    @staticmethod
    def _slugify_legend(legend: str | None) -> str | None:
        """
        Convert legend to valid Python identifier.

        Converts a human-readable legend (e.g., "Personal Information")
        to a valid Python identifier (e.g., "personal_information") for
        use as FormCollection attribute names.

        Args:
            legend: The legend text to slugify

        Returns:
            str | None: Slugified version, or None if legend is None/empty

        Example:
            >>> FormFactory._slugify_legend('Personal Information')
            'personal_information'
            >>> FormFactory._slugify_legend(None)
            None
        """
        if not legend:
            return None
        import re

        slug = re.sub(r'[^a-z0-9]+', '_', legend.lower())
        slug = slug.strip('_')
        return slug or None

    @staticmethod
    def _get_non_model_fields_from_base(base_form: type | None, model: type[models.Model]) -> list[str]:
        """
        Get list of non-model field names declared on base_form.

        These are fields defined directly on the form class that don't correspond
        to model fields (like password1, password2 on UserCreationForm).

        Args:
            base_form: The base form class to inspect
            model: The model class

        Returns:
            List of non-model field names declared on base_form

        Example:
            >>> FormFactory._get_non_model_fields_from_base(UserCreationForm, User)
            ['password1', 'password2']
        """
        if not base_form:
            return []

        non_model_fields = []

        # Get declared fields from the base form (not inherited from ModelForm)
        if hasattr(base_form, 'declared_fields'):
            for field_name in base_form.declared_fields.keys():
                # Check if this field is NOT a model field
                if not FormFactory._is_model_field(field_name, model):
                    non_model_fields.append(field_name)

        return non_model_fields

    @staticmethod
    def _exclude_unused_non_model_fields(
        form_class: type,
        used_field_names: list[str],
        non_model_fields: list[str],
    ) -> type:
        """
        Remove non-model fields from form_class that are not in used_field_names.

        When inheriting from a base form with non-model fields (e.g., UserCreationForm
        with password1, password2), we need to explicitly exclude non-model fields that
        are not used in the current Fieldset/Row to prevent duplication.

        Args:
            form_class: The form class to modify
            used_field_names: List of field names actually used in this Fieldset/Row
            non_model_fields: List of all non-model field names from base form

        Returns:
            New form class with unused non-model fields set to None

        Example:
            # UserCreationForm has password1, password2
            # Fieldset only uses username, email
            # Result: password1=None, password2=None on the new form class
        """
        # Find non-model fields that are NOT used in this Fieldset/Row
        unused_non_model_fields = [field for field in non_model_fields if field not in used_field_names]

        if not unused_non_model_fields:
            return form_class  # No unused fields, return as-is

        # Create new form class that sets unused fields to None
        exclusions = dict.fromkeys(unused_non_model_fields)
        return type(
            form_class.__name__,
            (form_class,),
            exclusions,
        )

    @staticmethod
    def _create_single_field_form(
        field: Field,
        model: type[models.Model],
        base_form: type[ModelForm] | None = None,
    ) -> type[ModelForm]:
        """
        Create a Form containing a single field.

        This method creates a ModelForm with just one field, handling:
        - Non-model fields (from base_form) - properly inherited
        - Non-editable fields via Meta.disabled_fields
        - Field configurations (label, widget, required, etc.)
        - django-formset features (show_if, hide_if, calculate)

        Args:
            field: The Field definition from the layout
            model: The Django model class
            base_form: Optional base ModelForm class

        Returns:
            A ModelForm class with the single field configured

        Example:
            form_class = FormFactory._create_single_field_form(
                field=Field('name', label='Full Name'),
                model=Customer,
            )
            form = form_class()
        """
        from formset.forms import ModelForm as FormsetModelForm

        # Ensure base_form has FormsetMixin (if provided)
        if base_form:
            base = ensure_formset_mixin(base_form)
        else:
            base = FormsetModelForm

        # Get non-model fields from base form BEFORE creating the form
        non_model_fields_in_base = FormFactory._get_non_model_fields_from_base(base_form, model)

        # Check if field is a model field
        if not FormFactory._is_model_field(field.name, model):
            # Non-model field - it should be defined on base_form
            # Create form with empty Meta.fields (inherits field from base_form)
            meta_attrs = {
                'model': model,
                'fields': [],
            }
        else:
            # Check if field is non-editable
            is_disabled = FormFactory._is_field_non_editable(field.name, model)

            # Create Meta class
            if is_disabled:
                meta_attrs = {
                    'model': model,
                    'fields': [],  # Non-editable, use disabled_fields
                    'disabled_fields': [field.name],
                }
            else:
                meta_attrs = {
                    'model': model,
                    'fields': [field.name],  # Only this model field
                }

        meta_class = type('Meta', (), meta_attrs)

        # Create form
        form_attrs = {
            'Meta': meta_class,
            '_field_def': field,  # Store for __init__ customization
        }

        form_class = type(f'{model.__name__}{field.name.title()}Form', (base,), form_attrs)

        # CRITICAL: Exclude unused non-model fields to prevent duplication
        # For single-field forms, all non-model fields EXCEPT the current one should be excluded
        used_field_names = [field.name] if not FormFactory._is_model_field(field.name, model) else []
        form_class = FormFactory._exclude_unused_non_model_fields(
            form_class,
            used_field_names,
            non_model_fields_in_base,
        )

        # Customize __init__ to apply Field configurations
        original_init = form_class.__init__

        def custom_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if hasattr(self, 'fields'):
                FormFactory._apply_field_config(self.fields, self._field_def)

        form_class.__init__ = custom_init

        return form_class

    @staticmethod
    def _create_row_form(
        row: Row,
        model: type[models.Model],
        base_form: type[ModelForm] | None = None,
    ) -> type[ModelForm]:
        """
        Create a Form containing all fields in a Row.

        The form will be wrapped in a FormCollection with HorizontalFormRenderer
        to display fields side-by-side.

        Args:
            row: The Row definition from the layout
            model: The Django model class
            base_form: Optional base ModelForm class

        Returns:
            A ModelForm class with all row fields configured

        Example:
            form_class = FormFactory._create_row_form(
                row=Row(Field('first_name'), Field('last_name')),
                model=Customer,
            )
        """
        from formset.forms import ModelForm as FormsetModelForm

        # Ensure base_form has FormsetMixin (if provided)
        if base_form:
            base = ensure_formset_mixin(base_form)
        else:
            base = FormsetModelForm

        # Get non-model fields from base form BEFORE creating the form
        non_model_fields_in_base = FormFactory._get_non_model_fields_from_base(base_form, model)

        # Extract all fields from Row and separate editable from non-editable
        editable_field_names = []
        disabled_field_names = []
        all_used_field_names = []  # Track ALL fields used in this Row

        for field in row.fields:
            # Track non-model fields that ARE used in this Row
            if not FormFactory._is_model_field(field.name, model):
                all_used_field_names.append(field.name)
                continue  # Skip non-model fields for Meta.fields

            if FormFactory._is_field_non_editable(field.name, model):
                # Non-editable fields go ONLY in disabled_fields, NOT in fields
                disabled_field_names.append(field.name)
            else:
                # Editable fields go in fields
                editable_field_names.append(field.name)

        # Add model fields to all_used_field_names
        all_used_field_names.extend(editable_field_names)
        all_used_field_names.extend(disabled_field_names)

        # Create Meta class
        meta_attrs = {
            'model': model,
            'fields': editable_field_names,  # Only model fields
        }

        if disabled_field_names:
            meta_attrs['disabled_fields'] = disabled_field_names

        meta_class = type('Meta', (), meta_attrs)

        # Create form
        form_attrs = {
            'Meta': meta_class,
            '_row_fields': row.fields,  # Store for __init__ customization
        }

        form_class = type(f'{model.__name__}RowForm', (base,), form_attrs)

        # CRITICAL: Exclude unused non-model fields to prevent duplication
        form_class = FormFactory._exclude_unused_non_model_fields(
            form_class,
            all_used_field_names,
            non_model_fields_in_base,
        )

        # Customize __init__ to apply Field configurations
        original_init = form_class.__init__

        def custom_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if hasattr(self, 'fields'):
                for field_def in self._row_fields:
                    FormFactory._apply_field_config(self.fields, field_def)

        form_class.__init__ = custom_init

        return form_class

    @staticmethod
    def _create_fieldset_form(
        fieldset: Fieldset,
        model: type[models.Model],
        base_form: type[ModelForm] | None = None,
    ) -> type[ModelForm]:
        """
        Create a Form containing all fields in a Fieldset.

        Similar to _create_row_form but for Fieldsets (which only contain Field objects).

        Args:
            fieldset: The Fieldset definition from the layout
            model: The Django model class
            base_form: Optional base ModelForm class

        Returns:
            A ModelForm class with all fieldset fields configured

        Example:
            form_class = FormFactory._create_fieldset_form(
                fieldset=Fieldset('Personal', Field('first_name'), Field('last_name')),
                model=Customer,
            )
        """
        from formset.forms import ModelForm as FormsetModelForm

        # Ensure base_form has FormsetMixin (if provided)
        if base_form:
            base = ensure_formset_mixin(base_form)
        else:
            base = FormsetModelForm

        # Get non-model fields from base form BEFORE creating the form
        non_model_fields_in_base = FormFactory._get_non_model_fields_from_base(base_form, model)

        # Extract all fields from Fieldset and separate editable from non-editable
        editable_field_names = []
        disabled_field_names = []
        all_used_field_names = []  # Track ALL fields used in this Fieldset

        for field in fieldset.fields:
            # Track non-model fields that ARE used in this Fieldset
            if not FormFactory._is_model_field(field.name, model):
                all_used_field_names.append(field.name)
                continue  # Skip non-model fields for Meta.fields

            if FormFactory._is_field_non_editable(field.name, model):
                # Non-editable fields go ONLY in disabled_fields, NOT in fields
                disabled_field_names.append(field.name)
            else:
                # Editable fields go in fields
                editable_field_names.append(field.name)

        # Add model fields to all_used_field_names
        all_used_field_names.extend(editable_field_names)
        all_used_field_names.extend(disabled_field_names)

        # Create Meta class
        meta_attrs = {
            'model': model,
            'fields': editable_field_names,  # Only model fields
        }

        if disabled_field_names:
            meta_attrs['disabled_fields'] = disabled_field_names

        meta_class = type('Meta', (), meta_attrs)

        # Create form
        form_attrs = {
            'Meta': meta_class,
            '_fieldset_fields': fieldset.fields,  # Store for __init__ customization
        }

        fieldset_name = FormFactory._slugify_legend(fieldset.legend) or 'fieldset'
        form_class = type(f'{model.__name__}{fieldset_name.title()}Form', (base,), form_attrs)

        # CRITICAL: Exclude unused non-model fields to prevent duplication
        form_class = FormFactory._exclude_unused_non_model_fields(
            form_class,
            all_used_field_names,
            non_model_fields_in_base,
        )

        # Customize __init__ to apply Field configurations
        original_init = form_class.__init__

        def custom_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)

            # Apply field configuration from layout
            if hasattr(self, 'fields'):
                for field_def in self._fieldset_fields:
                    FormFactory._apply_field_config(self.fields, field_def)

        form_class.__init__ = custom_init

        return form_class

    @staticmethod
    def _process_field(
        item: Field,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Handle standalone Field (not in Fieldset/Row).

        Creates a single-field Form and adds it to the collection.

        Args:
            item: The Field to process
            collection_attrs: Dictionary to add processed items to
            model: The Django model class
            base_form: Optional base ModelForm class
            item_index: Index of this item in the parent's items list
        """
        # Create a form with just this one field
        form_class = FormFactory._create_single_field_form(
            field=item,
            model=model,
            base_form=base_form,
        )

        # Add form INSTANCE to collection (using field name as key)
        collection_attrs[item.name] = form_class()

    @staticmethod
    def _process_fieldset(
        item: Fieldset,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Handle Fieldset - creates a FormCollection or a single Form.

        Strategy:
        1. If Fieldset contains ONLY Field objects (no nested Fieldsets/Rows/Collections),
           create a single form with all fields (uses base_form if provided)
        2. If Fieldset contains nested structures (Fieldsets/Rows/Collections),
           create a FormCollection and process each item recursively

        Args:
            item: The Fieldset to process
            collection_attrs: Dictionary to add processed items to
            model: The Django model class
            base_form: Optional base ModelForm class (used for flat Fieldsets)
            item_index: Index of this item in the parent's items list
        """
        from djadmin_formset.renderers import DjAdminFormRenderer

        # Check if Fieldset contains only Field objects (no nested structures)
        has_only_fields = all(isinstance(f, Field) for f in item.fields)

        if has_only_fields and item.fields:
            # Flat fieldset with only fields -> create a single form
            fieldset_name = FormFactory._slugify_legend(item.legend) or f'fieldset_{item_index}'

            # Always create a form scoped to this Fieldset's fields
            # When base_form is provided, the created form extends it (inheriting non-model fields)
            # When base_form is None, creates a standard ModelForm
            form_class = FormFactory._create_fieldset_form(
                fieldset=item,
                model=model,
                base_form=base_form,  # Could be None or a form class
            )
            collection_attrs[fieldset_name] = form_class()
            return

        # Fieldset has nested structures (Fieldsets/Rows/Collections)
        # Create a FormCollection and process each item recursively
        fieldset_attrs = {
            'legend': item.legend,
            'default_renderer': DjAdminFormRenderer,
        }

        # Process each item in the Fieldset recursively
        for field_idx, field_item in enumerate(item.fields):
            FormFactory._process_layout_item(
                item=field_item,
                collection_attrs=fieldset_attrs,
                model=model,
                base_form=base_form,
                item_index=field_idx,
            )

        # Create FormCollection class for this Fieldset
        fieldset_name = FormFactory._slugify_legend(item.legend) or f'fieldset_{item_index}'

        fieldset_class = type(
            f'{model.__name__}{fieldset_name.title()}Fieldset',
            (FormCollection,),
            fieldset_attrs,
        )

        # Add FormCollection INSTANCE to parent collection
        collection_attrs[fieldset_name] = fieldset_class()

    @staticmethod
    def _process_row(
        item: Row,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Handle Row - creates a FormCollection with horizontal renderer.

        The Row's FormCollection contains a single Form with all the row's fields.
        Uses HorizontalFormRenderer to display fields side-by-side.

        Args:
            item: The Row to process
            collection_attrs: Dictionary to add processed items to
            model: The Django model class
            base_form: Optional base ModelForm class
            item_index: Index of this item in the parent's items list
        """
        from djadmin_formset.renderers import HorizontalFormRenderer

        # Create a single form with all fields in this row
        form_class = FormFactory._create_row_form(
            row=item,
            model=model,
            base_form=base_form,
        )

        # Create FormCollection with horizontal renderer
        row_name = f'row_{item_index}'

        row_attrs = {
            'main': form_class(),  # Single form with all row fields
            'default_renderer': HorizontalFormRenderer,  # Horizontal layout
        }

        row_class = type(
            f'{model.__name__}Row{item_index}',
            (FormCollection,),
            row_attrs,
        )

        # Add Row FormCollection INSTANCE to parent
        collection_attrs[row_name] = row_class()

    @staticmethod
    def _process_collection(
        item: Collection,
        collection_attrs: dict,
        model: type[models.Model],
        base_form: type[ModelForm] | None,
        item_index: int,
    ):
        """
        Handle Collection - creates nested FormCollection for related objects.

        This is for inline editing (one-to-many / many-to-many relationships).

        Args:
            item: The Collection to process
            collection_attrs: Dictionary to add processed items to
            model: The Django model class (parent model, not collection's model)
            base_form: Optional base ModelForm class
            item_index: Index of this item in the parent's items list
        """
        # Create the nested collection using the existing _create_collection method
        nested_collection_class = FormFactory._create_collection(item)

        # Add Collection FormCollection INSTANCE to parent
        collection_attrs[item.name] = nested_collection_class()

    @staticmethod
    def _find_related_field(child_model: type, collection_def: Collection) -> str | None:
        """
        Find the FK field on the child model that points to the parent.

        This is needed so django-formset can automatically set the FK when saving
        child instances in a Collection.

        Args:
            child_model: The Collection's model (e.g., OrderItem)
            collection_def: The Collection definition

        Returns:
            Name of the FK field (e.g., 'order'), or None if not found

        Example:
            For Collection('items', model=OrderItem), if OrderItem has:
                order = models.ForeignKey(Order)
            Returns: 'order'
        """
        # Get all FK fields on the child model
        for field in child_model._meta.get_fields():
            if field.many_to_one and not field.auto_created:  # ForeignKey
                # This is a FK field - we need to check if it points to a compatible parent
                # In our architecture, we don't have access to the parent model here,
                # so we'll use a simple heuristic: find the first FK that's not in the
                # Collection's fields list (assuming the FK is implicit)
                if collection_def.fields and field.name not in collection_def.fields:
                    # This FK is not in the explicit fields list - likely the parent FK
                    return field.name

        # Fallback: If no FK found with heuristic, try to infer from related_name
        # This won't work in all cases, so returning None is safe
        return None

    @staticmethod
    def _create_collection(collection_def: Collection) -> type[FormCollection]:
        """
        Create a nested FormCollection class from a Collection definition.

        This method builds a FormCollection for inline editing of related objects.
        It contains a "main" form with support for disabled_fields (non-editable fields).

        It supports:
        - Simple fields list → creates a "main" form
        - Nested layout → recursively processes fields and creates main form
        - Min/max/extra siblings configuration
        - Sortable collections (drag-and-drop)
        - Non-editable fields (via Meta.disabled_fields)

        Args:
            collection_def: The Collection definition from the layout

        Returns:
            A FormCollection class (not instantiated)

        Example:
            collection_class = FormFactory._create_collection(
                Collection('orders',
                    model=Order,
                    fields=['order_number', 'status', 'total'],  # order_number may be editable=False
                    is_sortable=True,
                )
            )
            # Returns a FormCollection class for Order model
        """
        from formset.forms import ModelForm as FormsetModelForm

        # Build collection attributes
        nested_attrs = {
            'min_siblings': collection_def.min_siblings,
            'max_siblings': collection_def.max_siblings,
            'extra_siblings': collection_def.extra_siblings,
            'is_sortable': collection_def.is_sortable,
        }

        # Set related_field so django-formset can automatically set the FK
        # Django-formset uses this in construct_instance() to link child instances to parent
        # Example: For OrderItem model with FK 'order', this finds and sets related_field='order'
        related_field_name = FormFactory._find_related_field(collection_def.model, collection_def)
        if related_field_name:
            nested_attrs['related_field'] = related_field_name

        # Set legend (defaults to model's verbose_name_plural)
        if collection_def.legend:
            nested_attrs['legend'] = collection_def.legend
        else:
            nested_attrs['legend'] = collection_def.model._meta.verbose_name_plural

        # Process collection fields/layout
        if collection_def.layout:
            # Collection has nested layout - process hierarchically
            # This follows the same pattern as from_layout()
            for idx, item in enumerate(collection_def.layout.items):
                FormFactory._process_layout_item(
                    item=item,
                    collection_attrs=nested_attrs,
                    model=collection_def.model,
                    base_form=collection_def.form_class,
                    item_index=idx,
                )

        elif collection_def.fields:
            # Collection has simple fields list - create a "main" form
            simple_fields = []

            for field_spec in collection_def.fields:
                if isinstance(field_spec, str):
                    simple_fields.append(Field(field_spec))
                else:
                    simple_fields.append(field_spec)

            # Collect field names and separate editable from non-editable
            editable_field_names = []
            disabled_field_names = []

            for field in simple_fields:
                if FormFactory._is_field_non_editable(field.name, collection_def.model):
                    # Non-editable fields go ONLY in disabled_fields, NOT in fields
                    disabled_field_names.append(field.name)
                else:
                    # Editable fields go in fields
                    editable_field_names.append(field.name)

            # CRITICAL: Always include the primary key field in Collections as DISABLED
            # Django-formset needs this to bind forms to existing instances.
            # The PK must be disabled (not editable) but still included in forms
            # so it appears in initial data and gets submitted with POST data.
            pk_field_name = collection_def.model._meta.pk.name
            if pk_field_name not in disabled_field_names:
                disabled_field_names.append(pk_field_name)
            if pk_field_name not in editable_field_names:
                # Also add to fields list (django-formset requires it in Meta.fields)
                editable_field_names.insert(0, pk_field_name)

            # Create Meta class with disabled_fields if needed
            base_form = collection_def.form_class or FormsetModelForm
            meta_attrs = {
                'model': collection_def.model,
                'fields': editable_field_names,  # Includes PK + editable fields
            }

            if disabled_field_names:
                meta_attrs['disabled_fields'] = disabled_field_names  # django-formset feature

            meta_class = type('Meta', (), meta_attrs)

            # Create form class
            form_attrs = {
                'Meta': meta_class,
                '_collection_fields': simple_fields,  # Store for __init__ customization
            }

            # Add PK field explicitly as a hidden input if it's in disabled_fields
            # Django doesn't create PK fields by default, but we need it for instance binding
            if pk_field_name in disabled_field_names:
                from django.forms import HiddenInput, IntegerField

                form_attrs[pk_field_name] = IntegerField(
                    widget=HiddenInput,
                    required=False,  # Not required for CREATE operations
                    disabled=True,  # Can't be edited
                )

            main_form_class = type(
                f'{collection_def.model.__name__}CollectionMainForm',
                (base_form,),
                form_attrs,
            )

            # Customize __init__ to apply Field configurations
            original_init = main_form_class.__init__

            def custom_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                if hasattr(self, 'fields'):
                    for field_def in self._collection_fields:
                        FormFactory._apply_field_config(self.fields, field_def)

            main_form_class.__init__ = custom_init

            # Add form INSTANCE to collection
            nested_attrs['main'] = main_form_class()

        # Add retrieve_instance method to get child instances from initial data
        def retrieve_instance(self, data):
            """
            Retrieve the instance for this collection sibling.

            Django-formset calls this during full_clean() for each sibling in
            a Collection (has_many=True). The default implementation returns
            self.instance (the parent), but we need to return the CHILD instance
            so that form.replicate() binds to the correct object.

            We match POST data to initial data by finding the sibling with the
            same 'id' field. This works because initial data is populated with
            model instances (including their PKs).

            Args:
                data: Dict with sibling data, e.g., {'main': {'id': 1, 'name': 'Updated'}}

            Returns:
                Model instance (child) to bind this sibling's forms to
            """
            # Extract PK from data (if present)
            pk = None
            if 'main' in data and 'id' in data['main']:
                pk = data['main']['id']

            # If we have a PK, fetch the existing instance from DB
            if pk:
                try:
                    return collection_def.model.objects.get(pk=pk)
                except collection_def.model.DoesNotExist:
                    # PK provided but instance doesn't exist - this is an error
                    # Fall through to create new instance (will likely fail with FK constraint)
                    pass

            # No PK or not found - return a new instance for CREATE
            return collection_def.model()

        nested_attrs['retrieve_instance'] = retrieve_instance

        # Create and return FormCollection class
        collection_class = type(
            f'{collection_def.model.__name__}Collection',
            (FormCollection,),
            nested_attrs,
        )

        return collection_class
