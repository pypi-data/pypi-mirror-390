# winipedia_django
(Some parts of the README are AI generated, so some parts might not be fully accurate)

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-5.2%2B-darkgreen)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive utility package for Django that provides efficient bulk operations, abstract base classes for management commands, and database utilities. Designed to simplify common Django operations while maintaining type safety and performance.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Modules](#core-modules)
  - [Bulk Operations](#bulk-operations)
  - [Management Commands](#management-commands)
  - [Database Utilities](#database-utilities)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [License](#license)

## Features

✨ **Efficient Bulk Operations**
- Bulk create, update, and delete with automatic chunking
- Multithreaded processing for improved performance
- Topological sorting for respecting model dependencies
- Cascade deletion simulation without database modifications

🎯 **Abstract Base Command**
- Template method pattern for consistent command structure
- Automatic logging of command options
- Pre-configured common arguments (dry-run, batch-size, threads, etc.)
- Type-safe command implementation

🗄️ **Database Utilities**
- Model introspection and field extraction
- Topological sorting of models by dependencies
- Raw SQL execution with parameter binding
- Model hashing for comparison operations
- Abstract BaseModel with timestamps

🔒 **Type Safety**
- Full type hints throughout the codebase
- Strict mypy configuration
- Compatible with modern Python type checking tools

## Installation

### Using pip

```bash
pip install winipedia-django
```

### Using Poetry

```bash
poetry add winipedia-django
```

### Using uv

```bash
uv pip install winipedia-django
```

### Requirements

- Python 3.12 or higher
- Django 5.2 or higher
- winipedia-utils 0.2.10 or higher

## Quick Start

### Basic Bulk Creation

```python
from winipedia_django.bulk import bulk_create_in_steps
from myapp.models import MyModel

# Create 10,000 objects efficiently
objects = [MyModel(name=f"item_{i}") for i in range(10000)]
created = bulk_create_in_steps(MyModel, objects, step=1000)
print(f"Created {len(created)} objects")
```

### Creating a Management Command

```python
from argparse import ArgumentParser
from typing import Any
from winipedia_django.command import ABCBaseCommand

class MyCommand(ABCBaseCommand):
    def add_command_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--input-file',
            type=str,
            required=True,
            help='Path to input file'
        )

    def handle_command(self, *args: Any, **options: Any) -> None:
        input_file = options['input_file']
        batch_size = options['batch_size']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be made')

        # Your command logic here
        self.stdout.write(self.style.SUCCESS('Command completed successfully'))
```

### Using Database Utilities

```python
from winipedia_django.database import (
    get_fields,
    topological_sort_models,
    BaseModel
)
from django.db import models

# Get all fields from a model
fields = get_fields(MyModel)
field_names = [f.name for f in fields if hasattr(f, 'name')]

# Sort models by dependencies
models_to_create = [Book, Author, Publisher]
sorted_models = topological_sort_models(models_to_create)
# Result: [Author, Publisher, Book] - dependencies first

# Use BaseModel for automatic timestamps
class Article(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        app_label = 'blog'
```

## Core Modules

### Bulk Operations

The `bulk` module provides efficient operations for handling large datasets in Django.

#### Key Functions

**`bulk_create_in_steps(model, bulk, step=1000)`**

Creates model instances in chunks with multithreading support.

```python
from winipedia_django.bulk import bulk_create_in_steps

users = [User(username=f"user_{i}", email=f"user_{i}@example.com")
         for i in range(5000)]
created_users = bulk_create_in_steps(User, users, step=500)
```

**`bulk_update_in_steps(model, bulk, update_fields, step=1000)`**

Updates model instances efficiently in chunks.

```python
from winipedia_django.bulk import bulk_update_in_steps

users = User.objects.all()[:1000]
for user in users:
    user.is_active = False

updated_count = bulk_update_in_steps(User, users, ['is_active'], step=500)
print(f"Updated {updated_count} users")
```

**`bulk_delete_in_steps(model, bulk, step=1000)`**

Deletes model instances in chunks, respecting cascade relationships.

```python
from winipedia_django.bulk import bulk_delete_in_steps

users_to_delete = User.objects.filter(is_inactive=True)[:1000]
total_deleted, deleted_by_model = bulk_delete_in_steps(User, users_to_delete)
print(f"Deleted {total_deleted} objects total")
print(f"Breakdown: {deleted_by_model}")
# Output: Breakdown: {'User': 1000, 'UserProfile': 1000, ...}
```

**`bulk_create_bulks_in_steps(bulk_by_class, step=1000)`**

Creates multiple model types respecting foreign key dependencies.

```python
from winipedia_django.bulk import bulk_create_bulks_in_steps

authors = [Author(name=f"Author {i}") for i in range(100)]
books = [Book(title=f"Book {i}", author=authors[0]) for i in range(500)]

bulk_by_class = {
    Author: authors,
    Book: books,
}

results = bulk_create_bulks_in_steps(bulk_by_class, step=100)
# Authors are created first, then books (respecting FK dependency)
print(f"Created {len(results[Author])} authors")
print(f"Created {len(results[Book])} books")
```

**`get_differences_between_bulks(bulk1, bulk2, fields)`**

Compares two lists of model instances and returns differences.

```python
from winipedia_django.bulk import get_differences_between_bulks
from winipedia_django.database import get_fields

bulk1 = [User(id=1, name="Alice"), User(id=2, name="Bob")]
bulk2 = [User(id=1, name="Alice"), User(id=3, name="Charlie")]

fields = get_fields(User)
only_in_1, only_in_2, common_1, common_2 = get_differences_between_bulks(
    bulk1, bulk2, fields
)

print(f"Only in bulk1: {len(only_in_1)}")  # Bob
print(f"Only in bulk2: {len(only_in_2)}")  # Charlie
print(f"In both: {len(common_1)}")         # Alice
```

**`simulate_bulk_deletion(model_class, entries)`**

Preview what would be deleted including cascade deletions, without modifying the database.

```python
from winipedia_django.bulk import simulate_bulk_deletion

users_to_delete = User.objects.filter(is_inactive=True)[:100]
deletion_preview = simulate_bulk_deletion(User, users_to_delete)

for model, objects in deletion_preview.items():
    print(f"{model.__name__}: {len(objects)} objects would be deleted")
```

### Management Commands

The `command` module provides an abstract base class for creating well-structured Django management commands.

#### ABCBaseCommand

A template method pattern implementation that enforces consistent command structure.

**Features:**
- Automatic logging of all command options
- Pre-configured common arguments
- Type-safe implementation
- Enforced abstract methods

**Common Arguments (automatically added):**
- `--dry-run`: Show what would be done without executing
- `--size`: Size parameter for operations
- `--force`: Force an action
- `--delete`: Enable deletion
- `--quiet`: Suppress non-error output
- `--debug`: Print debug output
- `--yes`: Answer yes to all prompts
- `--config`: Configuration file or JSON string
- `--timeout`: Timeout for operations
- `--batch-size`: Number of items per batch
- `--no-input`: Do not prompt for user input
- `--threads`: Number of threads for processing
- `--processes`: Number of processes for processing

**Example Implementation:**

```python
from argparse import ArgumentParser
from typing import Any
from winipedia_django.command import ABCBaseCommand

class ImportDataCommand(ABCBaseCommand):
    """Import data from a CSV file."""

    def add_command_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file to import'
        )
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            choices=['user', 'product', 'order'],
            help='Model to import data into'
        )

    def handle_command(self, *args: Any, **options: Any) -> None:
        """Execute the import command."""
        file_path = options['file']
        model_name = options['model']
        batch_size = options['batch_size'] or 1000
        dry_run = options['dry_run']
        threads = options['threads'] or 4

        if not dry_run:
            self.stdout.write(
                self.style.WARNING(f'Importing {model_name} from {file_path}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('DRY RUN - No changes will be made')
            )

        # Your import logic here
        self.stdout.write(
            self.style.SUCCESS('Import completed successfully')
        )
```

**Usage:**

```bash
# Normal execution
python manage.py import_data --file data.csv --model user --batch-size 500

# Dry run
python manage.py import_data --file data.csv --model user --dry-run

# With threading
python manage.py import_data --file data.csv --model user --threads 8

# Quiet mode
python manage.py import_data --file data.csv --model user --quiet
```

### Database Utilities

The `database` module provides utilities for working with Django models and the database.

#### Model Introspection

**`get_model_meta(model)`**

Get the Django model metadata options object.

```python
from winipedia_django.database import get_model_meta

meta = get_model_meta(User)
print(meta.db_table)  # 'auth_user'
print(meta.app_label)  # 'auth'
```

**`get_fields(model)`**

Get all fields from a model including relationships.

```python
from winipedia_django.database import get_fields

fields = get_fields(User)
for field in fields:
    if hasattr(field, 'name'):
        print(f"Field: {field.name}, Type: {type(field).__name__}")
```

**`get_field_names(fields)`**

Extract field names from field objects.

```python
from winipedia_django.database import get_fields, get_field_names

fields = get_fields(User)
field_names = get_field_names(fields)
print(field_names)  # ['id', 'username', 'email', 'is_active', ...]
```

#### Model Sorting

**`topological_sort_models(models)`**

Sort Django models in dependency order using topological sorting.

```python
from winipedia_django.database import topological_sort_models

# Models with dependencies
models = [Review, Book, Author, Publisher]
sorted_models = topological_sort_models(models)
# Result: [Author, Publisher, Book, Review]
# Dependencies are created before dependents
```

#### Database Operations

**`execute_sql(sql, params=None)`**

Execute raw SQL query and return column names with results.

```python
from winipedia_django.database import execute_sql

sql = "SELECT id, username FROM auth_user WHERE is_active = %(active)s"
params = {"active": True}
columns, rows = execute_sql(sql, params)

for row in rows:
    print(f"ID: {row[0]}, Username: {row[1]}")
```

#### Model Hashing

**`hash_model_instance(instance, fields)`**

Hash a model instance based on its field values for comparison.

```python
from winipedia_django.database import hash_model_instance, get_fields

user1 = User(name="Alice", email="alice@example.com")
user2 = User(name="Alice", email="alice@example.com")

fields = get_fields(User)
hash1 = hash_model_instance(user1, fields)
hash2 = hash_model_instance(user2, fields)

print(hash1 == hash2)  # True - same field values
```

#### BaseModel

An abstract base model with automatic timestamp fields.

```python
from winipedia_django.database import BaseModel
from django.db import models

class Article(BaseModel):
    """Article model with automatic timestamps."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)

    class Meta:
        app_label = 'blog'

    def __str__(self) -> str:
        return self.title

# Usage
article = Article(title="My Article", content="...", author="John")
article.save()

print(article.created_at)  # Automatically set
print(article.updated_at)  # Automatically set
print(str(article))  # Article(id=1, created_at=..., updated_at=..., title=My Article, ...)
```

## Usage Examples

### Example 1: Bulk Import with Progress Tracking

```python
from winipedia_django.bulk import bulk_create_in_steps
from myapp.models import Product
import csv

def import_products(csv_file):
    """Import products from CSV file."""
    products = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(Product(
                name=row['name'],
                price=float(row['price']),
                description=row['description']
            ))

    # Create in steps of 500
    created = bulk_create_in_steps(Product, products, step=500)
    print(f"Successfully imported {len(created)} products")
    return created
```

### Example 2: Efficient Data Synchronization

```python
from winipedia_django.bulk import get_differences_between_bulks
from winipedia_django.database import get_fields

def sync_users(remote_users, local_users):
    """Synchronize users between remote and local."""
    fields = get_fields(User)

    only_remote, only_local, common_remote, common_local = (
        get_differences_between_bulks(remote_users, local_users, fields)
    )

    # Create new users
    if only_remote:
        bulk_create_in_steps(User, only_remote)

    # Delete removed users
    if only_local:
        bulk_delete_in_steps(User, only_local)

    print(f"Created: {len(only_remote)}, Deleted: {len(only_local)}")
```

### Example 3: Safe Deletion Preview

```python
from winipedia_django.bulk import simulate_bulk_deletion

def preview_deletion(user_ids):
    """Preview what would be deleted."""
    users = User.objects.filter(id__in=user_ids)
    preview = simulate_bulk_deletion(User, list(users))

    print("Deletion Preview:")
    for model, objects in preview.items():
        print(f"  {model.__name__}: {len(objects)} objects")

    return preview
```

### Example 4: Complex Data Migration

```python
from winipedia_django.bulk import bulk_create_bulks_in_steps
from winipedia_django.database import topological_sort_models

def migrate_data(source_db):
    """Migrate data from source database."""
    # Fetch data from source
    authors = fetch_authors(source_db)
    publishers = fetch_publishers(source_db)
    books = fetch_books(source_db)

    # Create in dependency order
    bulk_by_class = {
        Author: authors,
        Publisher: publishers,
        Book: books,
    }

    results = bulk_create_bulks_in_steps(bulk_by_class, step=1000)

    for model, instances in results.items():
        print(f"Migrated {len(instances)} {model.__name__} objects")
```

## API Reference

### Bulk Module (`winipedia_django.bulk`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `bulk_create_in_steps()` | Create objects in chunks | `list[Model]` |
| `bulk_update_in_steps()` | Update objects in chunks | `int` (count) |
| `bulk_delete_in_steps()` | Delete objects in chunks | `tuple[int, dict]` |
| `bulk_create_bulks_in_steps()` | Create multiple models respecting dependencies | `dict[type[Model], list[Model]]` |
| `get_differences_between_bulks()` | Compare two model lists | `tuple[list, list, list, list]` |
| `simulate_bulk_deletion()` | Preview cascade deletions | `dict[type[Model], set[Model]]` |
| `multi_simulate_bulk_deletion()` | Preview deletions for multiple models | `dict[type[Model], set[Model]]` |

### Command Module (`winipedia_django.command`)

| Class | Purpose |
|-------|---------|
| `ABCBaseCommand` | Abstract base class for management commands |

### Database Module (`winipedia_django.database`)

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_model_meta()` | Get model metadata | `Options[Model]` |
| `get_fields()` | Get all model fields | `list[Field]` |
| `get_field_names()` | Extract field names | `list[str]` |
| `topological_sort_models()` | Sort models by dependencies | `list[type[Model]]` |
| `execute_sql()` | Execute raw SQL | `tuple[list[str], list[Any]]` |
| `hash_model_instance()` | Hash model instance | `int` |

| Class | Purpose |
|-------|---------|
| `BaseModel` | Abstract base model with timestamps |

## Best Practices

### 1. Bulk Operations

✅ **Do:**
- Use appropriate step sizes (default 1000 is usually good)
- Use `bulk_create_bulks_in_steps()` for related models
- Preview deletions with `simulate_bulk_deletion()` before actual deletion
- Use `--dry-run` flag in commands to test before executing

❌ **Don't:**
- Use bulk operations inside nested transactions without careful consideration
- Create very large bulks without chunking
- Ignore cascade deletion warnings

### 2. Management Commands

✅ **Do:**
- Use `--dry-run` for destructive operations
- Provide meaningful `--batch-size` options
- Use `--quiet` for automation scripts
- Log important operations

❌ **Don't:**
- Override `add_arguments()` or `handle()` methods
- Ignore the template method pattern
- Skip implementing abstract methods

### 3. Database Operations

✅ **Do:**
- Use `topological_sort_models()` when creating related models
- Use `get_fields()` for introspection instead of hardcoding field names
- Use `execute_sql()` with parameter binding for security
- Inherit from `BaseModel` for automatic timestamps

❌ **Don't:**
- Use raw string concatenation in SQL queries
- Assume field order in models
- Manually manage created_at/updated_at fields

## Performance Tips

1. **Adjust Step Size**: Larger steps are faster but use more memory
   ```python
   # For large objects, use smaller steps
   bulk_create_in_steps(LargeModel, objects, step=100)

   # For small objects, use larger steps
   bulk_create_in_steps(SmallModel, objects, step=5000)
   ```

2. **Use Threading**: Leverage multithreading for I/O-bound operations
   ```bash
   python manage.py my_command --threads 8
   ```

3. **Batch Processing**: Process data in batches to reduce memory usage
   ```python
   for batch in get_step_chunks(large_dataset, 1000):
       process_batch(batch)
   ```

## Contributing

Contributions are welcome! Please ensure:

- Code follows the project's style guide (enforced by ruff)
- All tests pass: `pytest`
- Type checking passes: `mypy`
- Code is documented with docstrings

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Made with ❤️ by Winipedia**
