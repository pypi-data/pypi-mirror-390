# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for TransformFileOperator.
"""

import pytest
from unittest.mock import patch
from airflow.exceptions import AirflowSkipException
from pristy.alfresco_operator.transform_file import TransformFileOperator


class TestTransformFileOperator:
    """Tests for TransformFileOperator."""

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_single_file(
        self, mock_var, sample_alfresco_node, mock_airflow_context
    ):
        """Test transforming a single file node."""
        mock_var.get.return_value = "https://alfresco.example.com"

        operator = TransformFileOperator(
            task_id="transform_file", child=[sample_alfresco_node]
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 1
        node = result[0]
        assert node["name"] == "test-document.pdf"
        assert node["type"] == "cm:content"
        assert node["dateCreated"] == "2024-01-15T10:30:00Z"
        assert node["owner"] == "admin"
        assert "source" in node
        assert node["source"]["type"] == "alfresco"
        assert node["source"]["server"] == "https://alfresco.example.com"
        assert node["source"]["uuid"] == "workspace://SpacesStore/node-uuid-123"
        assert node["source"]["mimetype"] == "application/pdf"
        assert node["source"]["size"] == 102400

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_multiple_files(self, mock_var, mock_airflow_context):
        """Test transforming multiple file nodes."""
        mock_var.get.return_value = "https://alfresco.example.com"

        files = [
            {
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
            },
            {
                "id": "node-2",
                "name": "doc2.docx",
                "nodeType": "cm:content",
                "isFile": True,
                "isFolder": False,
                "createdAt": "2024-01-02T11:00:00+0000",
                "modifiedAt": "2024-01-02T11:00:00+0000",
                "createdByUser": {"id": "user2"},
                "modifiedByUser": {"id": "user2"},
                "path": {"name": "/Company Home/Documents"},
                "content": {
                    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "sizeInBytes": 2048,
                },
            },
        ]

        operator = TransformFileOperator(task_id="transform_files", child=files)

        result = operator.execute(mock_airflow_context)

        assert len(result) == 2
        assert result[0]["name"] == "doc1.pdf"
        assert result[1]["name"] == "doc2.docx"

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_filelink(self, mock_var, mock_airflow_context):
        """Test transforming app:filelink node type."""
        mock_var.get.return_value = "https://alfresco.example.com"

        filelink = {
            "id": "link-uuid",
            "name": "link-to-doc.pdf",
            "nodeType": "app:filelink",
            "isFile": True,
            "isFolder": False,
            "createdAt": "2024-01-01T10:00:00+0000",
            "modifiedAt": "2024-01-01T10:00:00+0000",
            "createdByUser": {"id": "admin"},
            "modifiedByUser": {"id": "admin"},
            "path": {"name": "/Company Home/Links"},
        }

        operator = TransformFileOperator(task_id="transform_filelink", child=[filelink])

        result = operator.execute(mock_airflow_context)

        assert len(result) == 1
        node = result[0]
        assert node["source"]["type"] == "alfresco"
        assert node["source"]["uuid"] == "link-uuid"
        assert "mimetype" not in node["source"]
        assert "size" not in node["source"]

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_skips_folders(
        self, mock_var, sample_alfresco_folder, mock_airflow_context
    ):
        """Test that folders are skipped."""
        mock_var.get.return_value = "https://alfresco.example.com"

        operator = TransformFileOperator(
            task_id="transform_file", child=[sample_alfresco_folder]
        )

        with pytest.raises(AirflowSkipException):
            operator.execute(mock_airflow_context)

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_skips_file_without_content(self, mock_var, mock_airflow_context):
        """Test that files without content are skipped."""
        mock_var.get.return_value = "https://alfresco.example.com"

        file_no_content = {
            "id": "node-no-content",
            "name": "empty.pdf",
            "nodeType": "cm:content",
            "isFile": True,
            "isFolder": False,
            "createdAt": "2024-01-01T10:00:00+0000",
            "modifiedAt": "2024-01-01T10:00:00+0000",
            "createdByUser": {"id": "admin"},
            "modifiedByUser": {"id": "admin"},
            "path": {"name": "/Company Home/Documents"},
            "content": None,
        }

        operator = TransformFileOperator(
            task_id="transform_file", child=[file_no_content]
        )

        with pytest.raises(AirflowSkipException):
            operator.execute(mock_airflow_context)

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_with_custom_mapping_func(
        self, mock_var, sample_alfresco_node, mock_airflow_context
    ):
        """Test transform with custom mapping function."""
        mock_var.get.return_value = "https://alfresco.example.com"

        def custom_mapper(src_node, new_node):
            new_node["custom_field"] = "custom_value"
            new_node["properties"]["custom:prop"] = src_node["name"].upper()

        operator = TransformFileOperator(
            task_id="transform_file",
            child=[sample_alfresco_node],
            mapping_func=custom_mapper,
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 1
        node = result[0]
        assert node["custom_field"] == "custom_value"
        assert node["properties"]["custom:prop"] == "TEST-DOCUMENT.PDF"

    @patch("pristy.alfresco_operator.transform_file.Variable")
    def test_transform_empty_list(self, mock_var, mock_airflow_context):
        """Test transform with empty child list."""
        mock_var.get.return_value = "https://alfresco.example.com"

        operator = TransformFileOperator(task_id="transform_file", child=[])

        with pytest.raises(AirflowSkipException):
            operator.execute(mock_airflow_context)
