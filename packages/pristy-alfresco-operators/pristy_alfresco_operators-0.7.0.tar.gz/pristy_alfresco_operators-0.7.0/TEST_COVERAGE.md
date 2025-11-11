# Test Coverage Report

**Date**: 2025-10-16
**Version**: 0.4.1

## Summary

- **Total Operators**: 15 modules
- **Tested Modules**: 1 (JSON Schema validation only)
- **Code Coverage**: ~7% (estimated)

## Current Test Coverage

### ✅ Tested Components

| Component | Test File | Coverage |
|-----------|-----------|----------|
| JSON Schema validation | `tests/schema/test_schema.py` | ✅ Full |

### ❌ Missing Test Coverage

| Operator | Module | Priority | Complexity |
|----------|--------|----------|------------|
| `AlfrescoSearchOperator` | `search_node_operator.py` | 🔴 High | Medium |
| `AlfrescoFetchChildrenOperator` | `fetch_children_node_operator.py` | 🔴 High | Medium |
| `AlfrescoFetchNodeOperator` | `fetch_node_operator.py` | 🟡 Medium | Low |
| `AlfrescoFetchNodeExistOperator` | `fetch_node_exist_operator.py` | 🟡 Medium | Low |
| `AlfrescoFetchMetadaOperator` | `fetch_metadata_node_operator.py` | 🟡 Medium | Medium |
| `TransformFileOperator` | `transform_file.py` | 🔴 High | High |
| `TransformFolderOperator` | `transform_folder.py` | 🔴 High | High |
| `PushToKafkaOperator` | `push_node_to_kafka.py` | 🔴 High | High |
| `PushToDirectoryOperator` | `push_node_to_directory.py` | 🟡 Medium | Low |
| `CreateChildrenTableOperator` | `create_children_table.py` | 🟠 Important | Low |
| `SaveFolderToDbOperator` | `save_folder_to_db.py` | 🟠 Important | Medium |
| **Utility Functions** | | | |
| `update_state_db()` | `update_node_db.py` | 🔴 High | Medium |
| `update_node_path()` | `update_node_path.py` | 🔴 High | High |
| `parse_alfresco_pagination()` | `utils.py` | 🟠 Important | Low |
| `create_base_node()` | `utils.py` | 🔴 High | Medium |

## Recommended Test Strategy

### Phase 1: Critical Path Testing (Priority 🔴)

Focus on the most-used operators in typical DAG workflows:

1. **Search & Fetch**
   - `test_search_node_operator.py`
   - `test_fetch_children_node_operator.py`

2. **Transform**
   - `test_transform_file.py`
   - `test_transform_folder.py`

3. **Export**
   - `test_push_node_to_kafka.py`

4. **Utils**
   - `test_utils.py` (pagination, node creation)
   - `test_update_node_path.py`
   - `test_update_node_db.py`

### Phase 2: Database Operations (Priority 🟠)

5. **State Tracking**
   - `test_create_children_table.py`
   - `test_save_folder_to_db.py`

### Phase 3: Secondary Operators (Priority 🟡)

6. **Metadata & Existence**
   - `test_fetch_node_operator.py`
   - `test_fetch_node_exist_operator.py`
   - `test_fetch_metadata_node_operator.py`
   - `test_push_node_to_directory.py`

## Testing Challenges

### 1. External Dependencies

Most operators require external services:

- **Alfresco API**: HTTP connections, authentication
- **PostgreSQL**: Database connections
- **Kafka**: Message broker connections

**Solutions**:
- Use `pytest-mock` or `unittest.mock` for mocking
- Mock `HttpHook`, `PostgresHook`, `KafkaProducerHook`
- Create fixtures for common test data

### 2. Airflow Context

Operators depend on Airflow execution context:

**Solutions**:
- Create mock Airflow context fixture
- Mock `task_instance.xcom_pull()`
- Mock Airflow Variables

### 3. Database State

State tracking operators modify PostgreSQL:

**Solutions**:
- Use in-memory SQLite for testing
- Create test fixtures with sample data
- Clean up after each test

## Proposed Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── fixtures/
│   ├── alfresco_responses.py      # Mock Alfresco API responses
│   ├── nodes.py                   # Sample node data
│   └── airflow_context.py         # Mock Airflow context
├── unit/
│   ├── test_utils.py
│   ├── test_update_node_path.py
│   ├── test_update_node_db.py
│   ├── operators/
│   │   ├── test_search_node_operator.py
│   │   ├── test_fetch_children_node_operator.py
│   │   ├── test_transform_file.py
│   │   ├── test_transform_folder.py
│   │   ├── test_push_node_to_kafka.py
│   │   └── ...
│   └── ...
├── integration/
│   ├── test_search_and_transform.py
│   └── test_full_migration_workflow.py
└── schema/
    ├── test_schema.py             # ✅ Already exists
    ├── sample_nodes.json
    └── sample_fail_nodes.json
```

## Sample Test Implementation

### Example: Testing `create_base_node()`

```python
# tests/unit/test_utils.py
import pytest
from pristy.alfresco_operator.utils import create_base_node

def test_create_base_node_basic():
    """Test basic node creation from Alfresco source."""
    src_node = {
        'name': 'test.pdf',
        'nodeType': 'cm:content',
        'createdAt': '2024-01-15T10:30:00+0000',
        'modifiedAt': '2024-01-20T14:45:00+0000',
        'createdByUser': {'id': 'admin'},
        'modifiedByUser': {'id': 'editor'}
    }

    result = create_base_node(src_node)

    assert result['name'] == 'test.pdf'
    assert result['type'] == 'cm:content'
    assert result['dateCreated'] == '2024-01-15T10:30:00Z'
    assert result['owner'] == 'admin'
    assert result['properties']['cm:creator'] == 'admin'
    assert result['properties']['cm:modifier'] == 'editor'
```

### Example: Testing `AlfrescoSearchOperator`

```python
# tests/unit/operators/test_search_node_operator.py
import pytest
from unittest.mock import MagicMock, patch
from pristy.alfresco_operator.search_node_operator import AlfrescoSearchOperator

@pytest.fixture
def mock_http_response():
    """Mock Alfresco Search API response."""
    return {
        'list': {
            'entries': [
                {'entry': {'id': 'node-1', 'name': 'doc1.pdf'}},
                {'entry': {'id': 'node-2', 'name': 'doc2.pdf'}}
            ],
            'pagination': {
                'count': 2,
                'skipCount': 0,
                'maxItems': 100,
                'hasMoreItems': False
            }
        }
    }

@patch('pristy.alfresco_operator.search_node_operator.HttpHook')
def test_search_operator_basic(mock_hook, mock_http_response):
    """Test basic search with no pagination."""
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = mock_http_response
    mock_hook.return_value.run.return_value = mock_response

    # Create operator
    operator = AlfrescoSearchOperator(
        task_id='test_search',
        query="TYPE:'cm:content'",
        page_size=100
    )

    # Execute
    result = operator.execute({})

    # Assert
    assert len(result) == 2
    assert result[0]['id'] == 'node-1'
    assert result[1]['name'] == 'doc2.pdf'
```

## Coverage Goals

| Phase | Target Coverage | Timeline |
|-------|----------------|----------|
| Phase 1 | 60% | 2-3 days |
| Phase 2 | 75% | 1-2 days |
| Phase 3 | 85%+ | 1-2 days |

## Tools & Configuration

### Pytest Configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=pristy",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-branch",
]

[tool.coverage.run]
source = ["pristy"]
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Required Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

## Conclusion

Current test coverage is **minimal** (~7%). To reach production quality:

1. ✅ Schema validation tests exist
2. ❌ No operator tests
3. ❌ No utility function tests
4. ❌ No integration tests

**Recommendation**: Implement Phase 1 tests before next release (0.5.0) to cover critical data transformation path.
