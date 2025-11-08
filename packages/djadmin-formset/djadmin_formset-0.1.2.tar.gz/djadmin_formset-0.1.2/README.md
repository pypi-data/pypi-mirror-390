# djadmin-formset

Django-formset integration plugin for django-admin-deux Layout API.

## Overview

This plugin provides full [django-formset](https://github.com/jrief/django-formset) FormCollection support for the django-admin-deux Layout API, enabling advanced form features:

- **Inline Editing**: Collection components for related objects
- **Conditional Fields**: Show/hide fields based on other field values
- **Computed Fields**: Auto-calculate field values from expressions
- **Client-Side Validation**: Real-time validation without page refresh
- **Drag-and-Drop Ordering**: Sortable collections
- **Progressive Enhancement**: Works alongside core djadmin without breaking basic forms

## Installation

```bash
# Install from PyPI (when published)
pip install djadmin-formset

# Or install with django-admin-deux
pip install django-admin-deux[djadmin-formset]
```

## Configuration

### Automatic Configuration (Recommended)

Use `djadmin_apps()` for zero-configuration setup:

```python
# settings.py
from djadmin import djadmin_apps

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # ... other Django apps
    'myapp',
] + djadmin_apps()  # Automatically includes djadmin-formset in correct order
```

The plugin system automatically:
- Installs `djadmin_formset` BEFORE `djadmin` for template override
- Installs `formset` dependency
- Handles all ordering requirements

### Manual Configuration

If you need manual control over `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... Django apps ...
    'formset',           # django-formset (dependency)
    'djadmin_formset',   # MUST come BEFORE djadmin for template overrides
    'djadmin',
    # ...
]
```

**CRITICAL**: `djadmin_formset` MUST appear before `djadmin` in `INSTALLED_APPS`. This ensures Django's template loader finds the FormCollection templates before the standard form templates.

## Usage

### Basic Inline Editing

```python
from djadmin import ModelAdmin, register, Layout, Field, Collection

@register(Author)
class AuthorAdmin(ModelAdmin):
    layout = Layout(
        Field('name'),
        Field('birth_date'),
        Collection('books',
            model=Book,
            fields=['title', 'isbn', 'published_date'],
            is_sortable=True,
        ),
    )
```

### Conditional Fields

```python
from djadmin import ModelAdmin, register, Layout, Field

@register(Product)
class ProductAdmin(ModelAdmin):
    layout = Layout(
        Field('name'),
        Field('product_type'),
        Field('weight', show_if=".product_type === 'physical'"),
        Field('file_size', show_if=".product_type === 'digital'"),
    )
```

### Computed Fields

```python
from djadmin import ModelAdmin, register, Layout, Field, Row

@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    layout = Layout(
        Row(
            Field('quantity', css_classes=['flex-1']),
            Field('price', css_classes=['flex-1']),
            Field(
                'total',
                calculate='.quantity * .price',
                css_classes=['flex-1']
            ),
        ),
    )
```

## Features Provided

This plugin advertises the following features to the djadmin core:

- `collections` / `inlines` - Inline editing support
- `conditional_fields` - Show/hide field logic
- `computed_fields` - Auto-calculated fields

## Requirements

- Python 3.11+
- Django 5.2+
- django-admin-deux >= 0.1.0
- django-formset >= 1.3

## Development Status

**Status**: Alpha - Day 18 of Milestone 3 implementation (Phase 2 complete)

This plugin is under active development as part of Milestone 3 (Layout API & Django-Formset Integration).

**Completed**:
- ✅ FormFactory - converts layouts to FormCollections
- ✅ DjAdminFormRenderer - Tailwind CSS themed renderer
- ✅ Plugin hooks - mixin-based form conversion
- ✅ Template overrides - django-formset JS/CSS integration
- ✅ Integration tests - all features tested
- ✅ Comprehensive documentation - 5+ guides

**In Progress**:
- 📋 Final polish and release preparation (Days 19-20)

## Documentation

Comprehensive documentation available in the main django-admin-deux docs:

### Core Documentation
- [Layout API Overview](../docs/layout-api/index.md) - Layout API fundamentals
- [Layout Components Reference](../docs/layout-api/components.md) - All components
- [Django Admin Migration Guide](../docs/layout-api/django-admin-migration.md) - Migrating from Django admin
- [Layout Examples](../docs/layout-api/examples.md) - Common patterns

### Plugin Documentation
- [Layout Integration Guide](../docs/plugins/djadmin-formset/layout-integration.md) - How the plugin works
- [Inline Editing Guide](../docs/plugins/djadmin-formset/inline-editing.md) - Collections and nested forms
- [Conditional Fields Guide](../docs/plugins/djadmin-formset/conditional-fields.md) - Show/hide logic
- [Computed Fields Guide](../docs/plugins/djadmin-formset/computed-fields.md) - Auto-calculated values
- [Renderer Customization Guide](../docs/plugins/djadmin-formset/renderer-customization.md) - Custom styling

## License

MIT License - See LICENSE file for details
