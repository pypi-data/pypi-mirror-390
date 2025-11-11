# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Shared pytest fixtures for all tests.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_airflow_context():
    """Create a mock Airflow execution context."""
    return {
        "task_instance": MagicMock(),
        "dag": MagicMock(),
        "execution_date": "2024-01-15T10:00:00Z",
        "task": MagicMock(),
    }


@pytest.fixture
def sample_alfresco_node():
    """Sample Alfresco node with all required fields."""
    return {
        "id": "workspace://SpacesStore/node-uuid-123",
        "name": "test-document.pdf",
        "nodeType": "cm:content",
        "isFile": True,
        "isFolder": False,
        "createdAt": "2024-01-15T10:30:00+0000",
        "modifiedAt": "2024-01-20T14:45:00+0000",
        "createdByUser": {"id": "admin"},
        "modifiedByUser": {"id": "editor"},
        "content": {"mimeType": "application/pdf", "sizeInBytes": 102400},
        "path": {"name": "/Company Home/Sites/test-site/documentLibrary/Folder"},
        "aspectNames": ["cm:titled"],
        "properties": {
            "cm:title": "Test Document",
            "cm:description": "A test document",
        },
    }


@pytest.fixture
def sample_alfresco_folder():
    """Sample Alfresco folder node."""
    return {
        "id": "workspace://SpacesStore/folder-uuid-456",
        "name": "Test Folder",
        "nodeType": "cm:folder",
        "isFile": False,
        "isFolder": True,
        "createdAt": "2024-01-10T08:00:00+0000",
        "modifiedAt": "2024-01-15T12:30:00+0000",
        "createdByUser": {"id": "admin"},
        "modifiedByUser": {"id": "admin"},
        "path": {"name": "/Company Home/Sites/test-site/documentLibrary"},
        "parentId": "workspace://SpacesStore/parent-uuid",
        "aspectNames": [],
        "properties": {},
    }


@pytest.fixture
def sample_search_response():
    """Sample Alfresco Search API response."""
    return {
        "list": {
            "entries": [
                {
                    "entry": {
                        "id": "node-1",
                        "name": "doc1.pdf",
                        "nodeType": "cm:content",
                        "isFile": True,
                        "isFolder": False,
                        "createdAt": "2024-01-01T10:00:00+0000",
                        "modifiedAt": "2024-01-01T10:00:00+0000",
                        "createdByUser": {"id": "user1"},
                        "modifiedByUser": {"id": "user1"},
                        "path": {"name": "/Company Home/Documents"},
                        "content": {"mimeType": "application/pdf", "sizeInBytes": 1024},
                    }
                },
                {
                    "entry": {
                        "id": "node-2",
                        "name": "doc2.pdf",
                        "nodeType": "cm:content",
                        "isFile": True,
                        "isFolder": False,
                        "createdAt": "2024-01-02T11:00:00+0000",
                        "modifiedAt": "2024-01-02T11:00:00+0000",
                        "createdByUser": {"id": "user2"},
                        "modifiedByUser": {"id": "user2"},
                        "path": {"name": "/Company Home/Documents"},
                        "content": {"mimeType": "application/pdf", "sizeInBytes": 2048},
                    }
                },
            ],
            "pagination": {
                "count": 2,
                "skipCount": 0,
                "maxItems": 100,
                "hasMoreItems": False,
                "totalItems": 2,
            },
        }
    }


@pytest.fixture
def sample_pagination_response_with_more():
    """Sample pagination response indicating more pages available."""
    return {
        "list": {
            "entries": [
                {"entry": {"id": f"node-{i}", "name": f"doc{i}.pdf"}} for i in range(50)
            ],
            "pagination": {
                "count": 50,
                "skipCount": 0,
                "maxItems": 50,
                "hasMoreItems": True,
                "totalItems": 150,
            },
        }
    }


@pytest.fixture
def mock_http_hook():
    """Create a mock HttpHook."""
    mock = MagicMock()
    mock.method = "GET"
    mock.http_conn_id = "alfresco_api"
    return mock


@pytest.fixture
def mock_postgres_hook():
    """Create a mock PostgresHook."""
    mock = MagicMock()
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock.get_conn.return_value = mock_conn

    return mock


@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer."""
    mock = MagicMock()
    mock.flush.return_value = 0  # No messages in queue
    return mock
