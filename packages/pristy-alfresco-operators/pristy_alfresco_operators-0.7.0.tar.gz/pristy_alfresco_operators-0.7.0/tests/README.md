# Tests

This directory contains the test suite for pristy-alfresco-operators.

## Structure

```
tests/
├── conftest.py                          # Shared fixtures
├── unit/                                # Unit tests
│   ├── test_utils.py                    # Tests for utility functions
│   ├── test_update_node_path.py         # Tests for path update logic
│   └── operators/                       # Operator tests
│       ├── test_search_node_operator.py
│       └── test_transform_file.py
└── schema/                              # Schema validation tests
    └── test_schema.py
```

## Running Tests

### With Poetry

```bash
# Install test dependencies
poetry install --with test

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pristy --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_utils.py

# Run specific test
poetry run pytest tests/unit/test_utils.py::TestCreateBaseNode::test_create_base_node_with_valid_data

# Run with verbose output
poetry run pytest -v

# Generate HTML coverage report
poetry run pytest --cov=pristy --cov-report=html
# Open htmlcov/index.html in browser
```

### Without Poetry

```bash
# Install dependencies
pip install -e .
pip install pytest pytest-cov pytest-mock

# Run tests
pytest
```

## Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Using Fixtures

Common fixtures are defined in `conftest.py`:

```python
def test_my_operator(sample_alfresco_node, mock_airflow_context):
    # Use fixtures in your tests
    operator = MyOperator(task_id='test', node=sample_alfresco_node)
    result = operator.execute(mock_airflow_context)
    assert result is not None
```

### Mocking External Dependencies

Use `unittest.mock` to mock external services:

```python
from unittest.mock import patch, MagicMock

@patch('pristy.alfresco_operator.my_operator.HttpHook')
def test_with_mock(mock_hook_class):
    mock_hook = MagicMock()
    mock_hook_class.return_value = mock_hook
    # Your test code
```

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Utils | 95% | ✅ 100% |
| Operators | 85% | 🟡 40% |
| Overall | 80% | 🟡 45% |

## CI/CD

Tests are automatically run on:
- Pull requests
- Pushes to develop/main branches

Coverage reports are uploaded to the CI system.
