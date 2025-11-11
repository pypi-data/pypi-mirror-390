# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for AlfrescoSearchOperator.
"""

import pytest
from unittest.mock import MagicMock, patch
from pristy.alfresco_operator.search_node_operator import AlfrescoSearchOperator


class TestAlfrescoSearchOperator:
    """Tests for AlfrescoSearchOperator."""

    def test_search_basic(self, sample_search_response, mock_airflow_context):
        """Test basic search with no pagination."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = sample_search_response

        # Create operator
        operator = AlfrescoSearchOperator(
            task_id="test_search", query="TYPE:'cm:content'", page_size=100
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "node-1"
        assert result[0]["name"] == "doc1.pdf"
        assert result[1]["id"] == "node-2"
        assert result[1]["name"] == "doc2.pdf"

    def test_search_with_pagination(self, mock_airflow_context):
        """Test search with multiple pages."""
        # Setup mock responses
        page1_response = {
            "list": {
                "entries": [
                    {"entry": {"id": f"node-{i}", "name": f"doc{i}.pdf"}}
                    for i in range(1, 51)
                ],
                "pagination": {
                    "count": 50,
                    "skipCount": 0,
                    "maxItems": 50,
                    "hasMoreItems": True,
                },
            }
        }

        page2_response = {
            "list": {
                "entries": [
                    {"entry": {"id": f"node-{i}", "name": f"doc{i}.pdf"}}
                    for i in range(51, 76)
                ],
                "pagination": {
                    "count": 25,
                    "skipCount": 50,
                    "maxItems": 50,
                    "hasMoreItems": False,
                },
            }
        }

        mock_response1 = MagicMock()
        mock_response1.json.return_value = page1_response

        mock_response2 = MagicMock()
        mock_response2.json.return_value = page2_response

        # Create operator
        operator = AlfrescoSearchOperator(
            task_id="test_search",
            query="TYPE:'cm:content'",
            page_size=50,
            max_items=2000,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.side_effect = [mock_response1, mock_response2]

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert len(result) == 75
        assert result[0]["id"] == "node-1"
        assert result[74]["id"] == "node-75"

    def test_search_respects_max_items(self, mock_airflow_context):
        """Test that search stops when max_items limit is reached."""
        # With max_items=120 and page_size=50, should fetch 3 pages
        # Page 1: 50 items (total: 50)
        # Page 2: 50 items (total: 100)
        # Page 3: 20 items (total: 120) - stops here

        def create_page(start, count=50):
            return {
                "list": {
                    "entries": [
                        {"entry": {"id": f"node-{i}", "name": f"doc{i}.pdf"}}
                        for i in range(start, start + count)
                    ],
                    "pagination": {
                        "count": count,
                        "skipCount": start,
                        "maxItems": count,
                        "hasMoreItems": True,
                    },
                }
            }

        page1 = create_page(0, 50)
        page2 = create_page(50, 50)
        page3 = create_page(100, 20)  # Only 20 items on last page

        mock_response1 = MagicMock()
        mock_response1.json.return_value = page1
        mock_response2 = MagicMock()
        mock_response2.json.return_value = page2
        mock_response3 = MagicMock()
        mock_response3.json.return_value = page3

        # Create operator with max_items=120
        operator = AlfrescoSearchOperator(
            task_id="test_search",
            query="TYPE:'cm:content'",
            page_size=50,
            max_items=120,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.side_effect = [
            mock_response1,
            mock_response2,
            mock_response3,
        ]

        # Execute
        result = operator.execute(mock_airflow_context)

        # Should fetch exactly 120 items
        assert len(result) == 120
        assert operator.http_hook.run.call_count == 3
        # Check that last request had adjusted maxItems
        last_call_data = operator.http_hook.run.call_args_list[2][1]["json"]
        assert last_call_data["paging"]["maxItems"] == 20

    def test_search_with_custom_sort(
        self, sample_search_response, mock_airflow_context
    ):
        """Test search with custom sort parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_search_response

        # Create operator with custom sort
        operator = AlfrescoSearchOperator(
            task_id="test_search",
            query="TYPE:'cm:content'",
            sort_field="cm:name",
            sort_ascending=True,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        operator.execute(mock_airflow_context)

        # Verify sort parameters were used
        assert operator.sort_field == "cm:name"
        assert operator.sort_ascending is True

    def test_search_empty_results(self, mock_airflow_context):
        """Test search with no results."""
        empty_response = {
            "list": {
                "entries": [],
                "pagination": {
                    "count": 0,
                    "skipCount": 0,
                    "maxItems": 100,
                    "hasMoreItems": False,
                },
            }
        }

        mock_response = MagicMock()
        mock_response.json.return_value = empty_response

        # Create operator
        operator = AlfrescoSearchOperator(
            task_id="test_search", query="TYPE:'cm:nonexistent'"
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert len(result) == 0
