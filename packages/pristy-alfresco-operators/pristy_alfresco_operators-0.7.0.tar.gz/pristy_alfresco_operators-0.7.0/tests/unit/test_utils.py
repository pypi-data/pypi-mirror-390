# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for utility functions in pristy.alfresco_operator.utils
"""

import pytest
from unittest.mock import MagicMock
from pristy.alfresco_operator.utils import parse_alfresco_pagination, create_base_node


class TestParseAlfrescoPagination:
    """Tests for parse_alfresco_pagination function."""

    def test_pagination_with_more_items(self):
        """Test pagination when more items are available."""
        response = MagicMock()
        response.json.return_value = {
            "list": {
                "pagination": {
                    "count": 50,
                    "skipCount": 0,
                    "maxItems": 50,
                    "hasMoreItems": True,
                }
            }
        }

        result = parse_alfresco_pagination(response, page_size=50)

        assert result is not None
        assert result == {"skipCount": 50}

    def test_pagination_no_more_items(self):
        """Test pagination when no more items are available."""
        response = MagicMock()
        response.json.return_value = {
            "list": {
                "pagination": {
                    "count": 25,
                    "skipCount": 50,
                    "maxItems": 50,
                    "hasMoreItems": False,
                }
            }
        }

        result = parse_alfresco_pagination(response, page_size=50)

        assert result is None

    def test_pagination_calculates_next_skip(self):
        """Test that skipCount is correctly calculated."""
        response = MagicMock()
        response.json.return_value = {
            "list": {
                "pagination": {
                    "count": 100,
                    "skipCount": 200,
                    "maxItems": 100,
                    "hasMoreItems": True,
                }
            }
        }

        result = parse_alfresco_pagination(response, page_size=100)

        assert result == {"skipCount": 300}  # 200 + 100


class TestCreateBaseNode:
    """Tests for create_base_node function."""

    def test_create_base_node_with_valid_data(self, sample_alfresco_node):
        """Test creating base node from valid Alfresco node."""
        result = create_base_node(sample_alfresco_node)

        assert result["name"] == "test-document.pdf"
        assert result["type"] == "cm:content"
        assert result["dateCreated"] == "2024-01-15T10:30:00Z"
        assert result["owner"] == "admin"
        assert "path" in result
        assert result["path"] == {}

    def test_create_base_node_properties(self, sample_alfresco_node):
        """Test that properties are correctly set."""
        result = create_base_node(sample_alfresco_node)

        props = result["properties"]
        assert props["cm:created"] == "2024-01-15T10:30:00Z"
        assert props["cm:creator"] == "admin"
        assert props["cm:modified"] == "2024-01-20T14:45:00Z"
        assert props["cm:modifier"] == "editor"

    def test_create_base_node_timezone_conversion(self):
        """Test that +0000 timezone is converted to Z."""
        src_node = {
            "name": "test.pdf",
            "nodeType": "cm:content",
            "createdAt": "2024-01-15T10:30:00+0000",
            "modifiedAt": "2024-01-20T14:45:00+0000",
            "createdByUser": {"id": "admin"},
            "modifiedByUser": {"id": "editor"},
        }

        result = create_base_node(src_node)

        assert result["dateCreated"] == "2024-01-15T10:30:00Z"
        assert result["properties"]["cm:created"] == "2024-01-15T10:30:00Z"
        assert result["properties"]["cm:modified"] == "2024-01-20T14:45:00Z"

    def test_create_base_node_different_users(self):
        """Test node creation when creator and modifier are different."""
        src_node = {
            "name": "document.doc",
            "nodeType": "cm:content",
            "createdAt": "2024-01-01T00:00:00+0000",
            "modifiedAt": "2024-01-02T00:00:00+0000",
            "createdByUser": {"id": "creator"},
            "modifiedByUser": {"id": "modifier"},
        }

        result = create_base_node(src_node)

        assert result["owner"] == "creator"
        assert result["properties"]["cm:creator"] == "creator"
        assert result["properties"]["cm:modifier"] == "modifier"

    def test_create_base_node_folder(self, sample_alfresco_folder):
        """Test creating base node from folder."""
        result = create_base_node(sample_alfresco_folder)

        assert result["name"] == "Test Folder"
        assert result["type"] == "cm:folder"
        assert result["dateCreated"] == "2024-01-10T08:00:00Z"
        assert result["owner"] == "admin"
