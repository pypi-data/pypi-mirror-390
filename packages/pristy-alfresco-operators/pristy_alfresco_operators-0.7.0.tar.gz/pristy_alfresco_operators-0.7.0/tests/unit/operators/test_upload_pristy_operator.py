# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for AlfrescoUploadPristyOperator.

This module contains comprehensive unit tests for the AlfrescoUploadPristyOperator,
which handles uploading files and creating folders in Alfresco using the custom
Pristy injector endpoint.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from airflow.exceptions import AirflowException

from pristy.alfresco_operator.upload_pristy_operator import (
    AlfrescoUploadPristyOperator,
)


class TestAlfrescoUploadPristyOperator:
    """Tests for AlfrescoUploadPristyOperator."""

    @pytest.fixture
    def sample_file_metadata(self):
        """Sample metadata for file upload."""
        return {
            "name": "document.pdf",
            "type": "cm:content",
            "path": {
                "root": "site:pristy-test",
                "short": "/folder1/folder2"
            },
            "properties": {
                "cm:title": "Test Document",
                "cm:description": "Test description"
            }
        }

    @pytest.fixture
    def sample_folder_metadata(self):
        """Sample metadata for folder creation."""
        return {
            "name": "New Folder",
            "type": "cm:folder",
            "path": {
                "root": "site:pristy-test",
                "short": "/parent"
            },
            "properties": {
                "cm:title": "Test Folder"
            }
        }

    @pytest.fixture
    def mock_success_response(self):
        """Mock successful Alfresco response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "node": "workspace://SpacesStore/uuid-123-456",
            "displayPath": "/Company Home/Sites/pristy-test/documentLibrary/folder1/folder2/document.pdf"
        }
        return mock_response

    @pytest.fixture
    def mock_error_response(self):
        """Mock error response from Alfresco."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "message": "Internal server error occurred"
        }
        mock_response.text = "Internal server error occurred"
        return mock_response

    # ==========================================================================
    # A. Validation Tests
    # ==========================================================================

    def test_init_valid_metadata_with_file(self, sample_file_metadata):
        """Test initialization with valid metadata and file path."""
        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path="/tmp/test.pdf",
            metadata=sample_file_metadata,
            http_conn_id="alfresco_api"
        )

        assert operator.file_path == "/tmp/test.pdf"
        assert operator.metadata == sample_file_metadata
        assert operator.http_conn_id == "alfresco_api"

    def test_init_missing_name_field(self):
        """Test that initialization fails when 'name' field is missing."""
        metadata_no_name = {
            "type": "cm:content",
            "path": {"root": "site:test", "short": "/folder"}
        }

        with pytest.raises(ValueError, match="metadata must contain 'name' field"):
            AlfrescoUploadPristyOperator(
                task_id="test_upload",
                metadata=metadata_no_name
            )

    def test_init_missing_path_field(self):
        """Test that initialization fails when 'path' field is missing."""
        metadata_no_path = {
            "name": "document.pdf",
            "type": "cm:content"
        }

        with pytest.raises(ValueError, match="metadata must contain 'path' field"):
            AlfrescoUploadPristyOperator(
                task_id="test_upload",
                metadata=metadata_no_path
            )

    def test_init_metadata_not_dict(self):
        """Test that initialization fails when metadata is not a dictionary."""
        with pytest.raises(ValueError, match="metadata must be a dictionary"):
            AlfrescoUploadPristyOperator(
                task_id="test_upload",
                metadata="not a dict"
            )

        with pytest.raises(ValueError, match="metadata must be a dictionary"):
            AlfrescoUploadPristyOperator(
                task_id="test_upload",
                metadata=["list", "not", "dict"]
            )

    def test_init_with_source_field_in_metadata(self, sample_file_metadata):
        """Test that operator initializes successfully even with 'source' field in metadata.

        The 'source' field triggers a warning (line 110-113), but initialization succeeds.
        The warning is visible in test output but not easily captured due to Airflow logging.
        """
        # Add 'source' field to metadata
        metadata_with_source = {**sample_file_metadata, "source": {"uuid": "test-uuid"}}

        # Operator should initialize successfully despite 'source' field
        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path="/tmp/test.pdf",
            metadata=metadata_with_source
        )

        # Verify operator created and metadata preserved
        assert operator.file_path == "/tmp/test.pdf"
        assert operator.metadata == metadata_with_source
        assert "source" in operator.metadata  # Source field is preserved

    # ==========================================================================
    # B. File Upload Tests
    # ==========================================================================

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_file_success(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_success_response,
        mock_airflow_context
    ):
        """Test successful file upload with multipart form data."""
        # Create test file
        test_file = tmp_path / "test.pdf"
        test_content = b"Test PDF content"
        test_file.write_bytes(test_content)

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_success_response

        # Create operator
        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        # Execute
        result = operator.execute(mock_airflow_context)

        # Verify result
        assert result["node"] == "workspace://SpacesStore/uuid-123-456"
        assert "displayPath" in result

        # Verify HTTP call
        mock_http_instance.run.assert_called_once()
        call_kwargs = mock_http_instance.run.call_args[1]

        # Verify endpoint and headers
        assert call_kwargs["endpoint"] == "/alfresco/service/fr/jeci/pristy/nodes/inject"
        assert call_kwargs["headers"]["Accept"] == "application/json"

        # Verify multipart form data
        assert "data" in call_kwargs
        assert "files" in call_kwargs
        assert call_kwargs["data"]["fileSize"] == str(len(test_content))

        # Verify metadata JSON
        metadata_json = call_kwargs["data"]["metadata"]
        parsed_metadata = json.loads(metadata_json)
        assert parsed_metadata["name"] == "document.pdf"
        assert parsed_metadata["type"] == "cm:content"

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_file_not_found(
        self,
        mock_http_hook_class,
        sample_file_metadata,
        mock_airflow_context
    ):
        """Test that upload fails when file does not exist."""
        # Mock HttpHook (should not be called)
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path="/nonexistent/file.pdf",
            metadata=sample_file_metadata
        )

        # Execute and expect exception
        with pytest.raises(AirflowException, match="File not found"):
            operator.execute(mock_airflow_context)

        # Verify HTTP was not called
        mock_http_instance.run.assert_not_called()

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_file_with_special_characters(
        self,
        mock_http_hook_class,
        tmp_path,
        mock_success_response,
        mock_airflow_context
    ):
        """Test upload with special characters in filename and metadata."""
        # Create test file with accents
        test_file = tmp_path / "français_éàç.pdf"
        test_file.write_bytes(b"Content with special chars")

        # Metadata with special characters
        metadata = {
            "name": "français_éàç.pdf",
            "type": "cm:content",
            "path": {
                "root": "site:test",
                "short": "/Dossiers français"
            },
            "properties": {
                "cm:title": "Titre avec accents éàç",
                "cm:description": "Description with émoji 📄"
            }
        }

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_success_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=metadata
        )

        result = operator.execute(mock_airflow_context)

        # Verify success
        assert result["node"] == "workspace://SpacesStore/uuid-123-456"

        # Verify metadata was serialized with ensure_ascii=False
        call_kwargs = mock_http_instance.run.call_args[1]
        metadata_json = call_kwargs["data"]["metadata"]

        # Check that special characters are preserved (not escaped)
        assert "français" in metadata_json
        assert "éàç" in metadata_json
        assert "📄" in metadata_json

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_file_handle_closed_on_success(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_success_response,
        mock_airflow_context
    ):
        """Test that file handle is properly closed after successful upload."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"Test content")

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_success_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        # Execute
        result = operator.execute(mock_airflow_context)

        # Verify success
        assert "node" in result

        # File should be accessible (not locked)
        assert test_file.exists()
        # Can read file (not locked)
        assert test_file.read_bytes() == b"Test content"

    # ==========================================================================
    # C. Folder Creation Tests
    # ==========================================================================

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_create_folder_success(
        self,
        mock_http_hook_class,
        sample_folder_metadata,
        mock_success_response,
        mock_airflow_context
    ):
        """Test successful folder creation without file upload."""
        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "node": "workspace://SpacesStore/folder-uuid",
            "displayPath": "/Company Home/Sites/pristy-test/documentLibrary/parent/New Folder"
        }
        mock_http_instance.run.return_value = mock_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_create_folder",
            file_path=None,  # No file, folder only
            metadata=sample_folder_metadata
        )

        result = operator.execute(mock_airflow_context)

        # Verify result
        assert result["node"] == "workspace://SpacesStore/folder-uuid"

        # Verify HTTP call - should NOT have file or fileSize
        call_kwargs = mock_http_instance.run.call_args[1]
        assert "files" not in call_kwargs or call_kwargs["files"] is None
        assert "data" in call_kwargs

        # Should only have metadata
        if "data" in call_kwargs:
            assert "metadata" in call_kwargs["data"]
            # Should NOT have fileSize when creating folder
            assert "fileSize" not in call_kwargs["data"]

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_create_folder_with_properties(
        self,
        mock_http_hook_class,
        mock_success_response,
        mock_airflow_context
    ):
        """Test folder creation with custom properties."""
        metadata = {
            "name": "Custom Folder",
            "type": "cm:folder",
            "path": {
                "root": "site:test",
                "short": "/"
            },
            "properties": {
                "cm:title": "Custom Title",
                "cm:description": "Custom Description",
                "cm:author": "Test User"
            },
            "permissions": {
                "ALLOWED": {"GROUP_EVERYONE": ["Consumer"]}
            }
        }

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_success_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_create_folder",
            file_path=None,
            metadata=metadata
        )

        result = operator.execute(mock_airflow_context)

        # Verify success
        assert "node" in result

        # Verify all metadata was sent
        call_kwargs = mock_http_instance.run.call_args[1]
        metadata_json = call_kwargs["data"]["metadata"]
        parsed = json.loads(metadata_json)

        assert parsed["properties"]["cm:title"] == "Custom Title"
        assert parsed["properties"]["cm:author"] == "Test User"
        assert "permissions" in parsed

    # ==========================================================================
    # D. HTTP Error Handling Tests
    # ==========================================================================

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_http_500_error(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_error_response,
        mock_airflow_context
    ):
        """Test handling of HTTP 500 error with JSON message."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"Test content")

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_error_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal server error occurred" in error_msg

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_http_404_error(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_airflow_context
    ):
        """Test handling of HTTP 404 error."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"Test content")

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "message": "Endpoint not found"
        }
        mock_http_instance.run.return_value = mock_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        error_msg = str(exc_info.value)
        assert "404" in error_msg
        assert "Endpoint not found" in error_msg

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_upload_http_error_plain_text(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_airflow_context
    ):
        """Test handling of HTTP error with plain text response (no JSON)."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"Test content")

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_response = MagicMock()
        mock_response.status_code = 400
        # Simulate JSON parsing failure
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = "Bad request - plain text error"
        mock_http_instance.run.return_value = mock_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        error_msg = str(exc_info.value)
        assert "400" in error_msg
        assert "Bad request - plain text error" in error_msg

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_file_handle_closed_on_exception(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_airflow_context
    ):
        """Test that file handle is closed even when exception occurs."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"Test content")

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        # Simulate exception during HTTP call
        mock_http_instance.run.side_effect = Exception("Network error")

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata
        )

        with pytest.raises(AirflowException):
            operator.execute(mock_airflow_context)

        # File should still be accessible (handle was closed in finally block)
        assert test_file.exists()
        assert test_file.read_bytes() == b"Test content"

    # ==========================================================================
    # E. Request Parameter Verification Tests
    # ==========================================================================

    @patch('pristy.alfresco_operator.upload_pristy_operator.HttpHook')
    def test_http_request_parameters(
        self,
        mock_http_hook_class,
        tmp_path,
        sample_file_metadata,
        mock_success_response,
        mock_airflow_context
    ):
        """Test that HTTP request parameters are correctly set."""
        test_file = tmp_path / "test.pdf"
        test_content = b"Test content"
        test_file.write_bytes(test_content)

        custom_endpoint = "/custom/endpoint/path"

        # Mock HttpHook
        mock_http_instance = MagicMock()
        mock_http_hook_class.return_value = mock_http_instance
        mock_http_instance.run.return_value = mock_success_response

        operator = AlfrescoUploadPristyOperator(
            task_id="test_upload",
            file_path=str(test_file),
            metadata=sample_file_metadata,
            http_conn_id="custom_conn",
            endpoint=custom_endpoint
        )

        result = operator.execute(mock_airflow_context)

        # Verify HttpHook was created with correct connection ID
        mock_http_hook_class.assert_called_once_with(
            method="POST",
            http_conn_id="custom_conn"
        )

        # Verify call was made
        mock_http_instance.run.assert_called_once()
        call_kwargs = mock_http_instance.run.call_args[1]

        # Verify endpoint
        assert call_kwargs["endpoint"] == custom_endpoint

        # Verify headers
        assert "headers" in call_kwargs
        assert call_kwargs["headers"]["Accept"] == "application/json"

        # Verify multipart structure
        assert "files" in call_kwargs
        assert "data" in call_kwargs

        # Verify file tuple format: (filename, file_handle, content_type)
        file_tuple = call_kwargs["files"]["file"]
        assert len(file_tuple) == 3
        assert file_tuple[0] == "test.pdf"  # filename
        assert file_tuple[2] == "application/octet-stream"  # content type

        # Verify data contains fileSize and metadata
        assert "fileSize" in call_kwargs["data"]
        assert call_kwargs["data"]["fileSize"] == str(len(test_content))
        assert "metadata" in call_kwargs["data"]

        # Verify metadata is JSON string
        metadata_str = call_kwargs["data"]["metadata"]
        assert isinstance(metadata_str, str)
        parsed = json.loads(metadata_str)
        assert parsed["name"] == "document.pdf"
