# Development Conventions - pristy-alfresco-operators

This document defines the coding conventions and best practices for the development of the `pristy-alfresco-operators` library.

---

## 📋 Table of Contents

1. [Language](#language)
2. [Code Structure](#code-structure)
3. [Python](#python)
4. [Airflow Operators](#airflow-operators)
5. [Database](#database)
6. [Error Handling](#error-handling)
7. [Logging](#logging)
8. [Testing](#testing)
9. [Documentation](#documentation)
10. [Git](#git)
11. [Release Process](#release-process)

---

## 1. Language

### Everything in English

As an open-source library published on PyPI, **everything** must be in English:

- ✅ Variable names
- ✅ Function names
- ✅ Class names
- ✅ Comments
- ✅ Docstrings
- ✅ Documentation (README, guides)
- ✅ Commit messages
- ✅ Issue/PR descriptions
- ✅ Log messages

### Naming Conventions

**Files**: `{verb}_{object}_operator.py`
- Examples: `fetch_children_node_operator.py`, `push_node_to_kafka.py`

**Classes**: PascalCase with "Operator" suffix
- Examples: `AlfrescoFetchChildrenOperator`, `PushToKafkaOperator`

**Functions/Methods**: snake_case with descriptive verbs
- Examples: `fetch_children()`, `update_state_db()`, `paginate()`

**Variables**: snake_case, descriptive
- Examples: `parent_id`, `node_list`, `max_items`

**Constants**: UPPER_SNAKE_CASE
- Examples: `DEFAULT_PAGE_SIZE`, `MAX_RETRIES`

---

## 2. Code Structure

### Project Layout

```
pristy-alfresco-operators/
├── pristy/
│   ├── __init__.py
│   ├── alfresco_operator/
│   │   ├── __init__.py
│   │   ├── fetch_children_node_operator.py
│   │   ├── push_node_to_kafka.py
│   │   └── ...
│   └── schema/
│       └── node_injector.schema.json
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── scripts/
│   └── sync_user.py
├── LICENSES/
│   └── Apache-2.0.txt
├── pyproject.toml
├── README.md
├── CONVENTIONS.md
└── CHANGELOG.md
```

### Imports Order

1. Standard library
2. Third-party libraries
3. Airflow
4. Local imports

```python
# Standard library
import os
from typing import Any

# Third-party
import jsonschema

# Airflow
from airflow.models.baseoperator import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Local
from pristy.alfresco_operator.update_node_db import update_state_db
```

### SPDX License Headers

All source files must include the SPDX license header:

```python
# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0
```

---

## 3. Python

### Version
- Python **3.12** (strictly)
- Use modern type hints (PEP 604): `list[str]` instead of `List[str]`

### Code Style
- Follow **PEP 8**
- **Line length**: 120 characters maximum
- **Indentation**: 4 spaces

### Type Hints

Always annotate types for function signatures:

```python
def fetch_children(
    self,
    parent_id: str,
    page_size: int = 100
) -> list[dict[str, Any]]:
    """
    Fetch children nodes from a parent folder.

    :param parent_id: The UUID of the parent node
    :param page_size: Number of items per page
    :return: List of child nodes
    """
    ...
```

### Resource Management

Always use context managers or try/finally:

✅ **Good**:
```python
# Files
with open(file_path, 'rb') as f:
    content = f.read()

# Database
conn = postgres_hook.get_conn()
cur = conn.cursor()
try:
    cur.execute(query, params)
    conn.commit()
finally:
    cur.close()
    conn.close()
```

❌ **Bad**:
```python
f = open(file_path, 'rb')
content = f.read()
# Missing close

conn = postgres_hook.get_conn()
cur = conn.cursor()
cur.execute(query)
conn.commit()
# No cleanup on exception
```

---

## 4. Airflow Operators

### Base Structure

```python
from airflow.models.baseoperator import BaseOperator
from airflow.exceptions import AirflowSkipException

class MyCustomOperator(BaseOperator):
    """
    Short description of the operator.

    Longer description explaining what the operator does,
    its use case, and any important behavior.

    :param required_param: Description of required parameter
    :param optional_param: Description with default value (default: "value")
    """

    def __init__(
        self,
        *,
        required_param: str,
        optional_param: str = "default",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.required_param = required_param
        self.optional_param = optional_param

    def execute(self, context) -> Any:
        """
        Execute the operator logic.

        :param context: Airflow context dictionary
        :return: Result to be passed to downstream tasks
        """
        self.log.info(f"Starting {self.__class__.__name__}")

        if not self.required_param:
            raise AirflowSkipException("Required parameter is empty")

        result = self._do_work()

        self.log.info(f"Completed with {len(result)} items")
        return result

    def _do_work(self) -> list:
        """Private method for business logic."""
        ...
```

### Operator Guidelines

1. **Idempotency**: Operators should be idempotent when possible
2. **Logging**: Use appropriate log levels (debug, info, warning, error)
3. **Skip vs Fail**: Use `AirflowSkipException` for non-error empty results
4. **State tracking**: Update database state before and after operations
5. **Retries**: Design operators to be retry-safe

### Configuration

- Use Airflow **Variables** for configuration values
- Use Airflow **Connections** for external systems
- Provide sensible defaults where possible

```python
from airflow.models import Variable

topic = Variable.get('kafka_export_topic')
page_size = int(Variable.get('page_size', '100'))
```

---

## 5. Database

### SQL Security - CRITICAL

**NEVER** use f-strings or string concatenation for SQL queries.

❌ **FORBIDDEN**:
```python
# DANGER: SQL Injection
cur.execute(f"UPDATE {table} SET state = '{state}' WHERE id = '{id}'")
cur.execute("UPDATE table SET state = '" + state + "' WHERE id = '" + id + "'")
```

✅ **REQUIRED**:
```python
from psycopg2 import sql

# For VALUES: prepared statements with %s
cur.execute(
    "UPDATE table SET state = %s WHERE id = %s",
    (state, id)
)

# For IDENTIFIERS (table/column names): sql.Identifier()
query = sql.SQL("UPDATE {table} SET state = %s WHERE {key} = %s").format(
    table=sql.Identifier(table_name),
    key=sql.Identifier(column_name)
)
cur.execute(query, (state, id))

# For BATCH operations: executemany()
cur.executemany(
    "INSERT INTO table (col1, col2) VALUES (%s, %s)",
    [(val1, val2), (val3, val4)]
)
```

### State Tracking Pattern

All tracking tables should have:
- A `state` column (varchar): `new` → `running` → `success` / `error`
- A unique identifier (uuid, id)

```python
def update_state_db(
    child_id: str,
    state: str,
    table_name: str = "export_alfresco_folder_children",
    source_key: str = "uuid"
) -> None:
    """
    Update the state of a node in the tracking database.

    :param child_id: Unique identifier of the node
    :param state: New state value
    :param table_name: Name of the tracking table
    :param source_key: Column name used as identifier
    """
    from psycopg2 import sql

    postgres_hook = PostgresHook(postgres_conn_id="local_pg")
    conn = postgres_hook.get_conn()
    cur = conn.cursor()
    try:
        query = sql.SQL("UPDATE {table} SET state = %s WHERE {key} = %s").format(
            table=sql.Identifier(table_name),
            key=sql.Identifier(source_key)
        )
        cur.execute(query, (state, child_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()
```

---

## 6. Error Handling

### Airflow Exceptions

Use appropriate Airflow exceptions:

```python
from airflow.exceptions import AirflowSkipException, AirflowFailException

# Skip: task is skipped (not an error)
if not data:
    raise AirflowSkipException('No data to process')

# Fail: definitive failure
if critical_error:
    raise AirflowFailException('Critical error occurred')

# RuntimeError: failure with retry
if retriable_error:
    raise RuntimeError('Temporary error, can retry')
```

### Error Handling Pattern

```python
def execute(self, context):
    local_id = None
    try:
        local_id = self._get_tracking_id()

        result = self._do_work()

        if local_id:
            update_state_db(local_id, "success")
        return result

    except Exception as ex:
        self.log.error(
            f"Error processing {local_id}: {type(ex).__name__}",
            exc_info=True
        )

        if local_id:
            update_state_db(local_id, f"error: {str(ex)[:100]}")

        raise RuntimeError(f"Processing failed: {ex}") from ex
```

### Error Messages

Provide clear, contextual error messages:

✅ **Good**:
```python
raise RuntimeError(
    f"Failed to load file {file_path}: "
    f"folder type {folder_type} not found in classification plan"
)
```

❌ **Bad**:
```python
raise RuntimeError("Error")
raise KeyError(folder_type)  # No context
```

---

## 7. Logging

### Log Levels

```python
# DEBUG: Technical details for debugging
self.log.debug(f"Parameters: {params}")

# INFO: Normal processing steps
self.log.info(f"Processing {count} items")

# WARNING: Abnormal but non-blocking situation
self.log.warning(f"Item {id} skipped: no files found")

# ERROR: Error requiring attention
self.log.error(f"Failed to connect to Alfresco: {error}")
```

### Informative Logs

Include metrics in logs:

```python
self.log.info(
    f"Processing completed: "
    f"{success_count} successful, "
    f"{error_count} errors, "
    f"{skip_count} skipped, "
    f"duration: {duration:.2f}s"
)
```

### Avoid Excessive Logging

❌ **Bad**: Log every item in a loop
```python
for item in items:  # If items has 10000 elements...
    self.log.info(f"Processing {item}")  # 10000 log lines!
```

✅ **Good**: Log statistics
```python
self.log.info(f"Processing {len(items)} items")
for i, item in enumerate(items):
    if i % 100 == 0:
        self.log.info(f"Progress: {i}/{len(items)}")
    # Process...
```

---

## 8. Testing

### Test Structure

```
tests/
├── __init__.py
├── test_operators.py
├── test_utils.py
└── schema/
    └── test_schema.py
```

### Test Naming

```python
def test_fetch_children_success():
    """Test fetching children with valid parent ID."""
    ...

def test_fetch_children_with_invalid_parent():
    """Test fetching children with invalid parent ID."""
    ...

def test_push_kafka_skip_when_empty():
    """Test that PushToKafkaOperator skips when no nodes."""
    ...
```

### Test Coverage

For each operator:
- ✅ Happy path test
- ✅ Error cases (invalid data, unavailable resources)
- ✅ Skip behavior (if applicable)
- ✅ Idempotency (if applicable)

### Running Tests

```bash
# Install test dependencies
uv sync --group test

# Run all tests with coverage
uv run pytest

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=pristy --cov-report=html
```

---

## 9. Documentation

### README.md

The README should include:

```markdown
# pristy-alfresco-operators

Short description of the library.

## Installation

pip install pristy-alfresco-operators

## Features

- Feature 1
- Feature 2

## Usage

### Basic Example

[Code example]

### Available Operators

Brief description of each operator

## Configuration

Required Airflow variables and connections

## Development

Instructions for local development setup

## Testing

Instructions for running tests

## License

Apache 2.0
```

### Docstrings

Use reStructuredText format with type annotations:

```python
def my_function(param1: str, param2: int = 10) -> list[str]:
    """
    Short description of the function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    :param param1: Description of parameter
    :param param2: Description with default value
    :return: Description of return value
    :raises ValueError: When this exception is raised
    """
```

### CHANGELOG.md

Maintain a changelog following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description

## [0.4.1] - 2025-10-16

### Security
- Fixed SQL injection in update_state_db

### Changed
- Improved connection handling with try/finally
```

---

## 10. Git

### Branches

- `main`: Stable production releases
- `develop`: Development branch
- `feature/{name}`: New features
- `fix/{name}`: Bug fixes
- `hotfix/{name}`: Urgent production fixes

### Commit Messages

Format: `{type}: {short description}`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `security`: Security fix
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Add/modify tests
- `docs`: Documentation
- `chore`: Maintenance tasks
- `build`: Build system changes

**Examples**:
```
feat: add pagination support to search operator
fix: correct SQL injection in save_folder_to_db
security: prevent SQL injection with parameterized queries
refactor: extract common pagination logic
docs: add usage examples to README
test: add unit tests for push_node_to_kafka
```

### Pull Requests

PR description should include:
- Summary of changes
- Related issue number (if applicable)
- Testing performed
- Breaking changes (if any)

---

## 11. Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New backward-compatible functionality
- **PATCH**: Backward-compatible bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Update `README.md` if needed
4. Run tests: `uv sync --group test && uv run pytest`
5. Create commit and tag:
   ```bash
   TAG=0.4.2
   git add pyproject.toml CHANGELOG.md
   git commit -m "version $TAG"
   git tag "$TAG"
   git push
   git push origin "tags/$TAG"
   ```
6. Build and publish:
   ```bash
   uv build
   uv publish
   ```

### Publishing to PyPI

Requirements:
- PyPI account
- PyPI token configured (via `uv publish --token` or environment variable)
- All tests passing
- Documentation updated

---

## 📚 References

- [Apache Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Version**: 1.0
**Last Updated**: 2025-10-16
