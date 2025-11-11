# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for AlfrescoDownloadContentOperator.
"""

import hashlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch
from airflow.exceptions import AirflowException

from pristy.alfresco_operator.download_content_operator import (
    AlfrescoDownloadContentOperator,
)


class TestAlfrescoDownloadContentOperator:
    """Tests for AlfrescoDownloadContentOperator."""

    def test_download_with_sha1_checksum(self, tmp_path, mock_airflow_context):
        """Test downloading a file with SHA1 checksum calculation."""
        # Prepare test data
        test_content = b"This is test file content for SHA1 hashing"
        expected_sha1 = hashlib.sha1(test_content).hexdigest()
        node_uuid = "test-uuid-123"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            filename="{uuid}.bin",
            calculate_checksum=True,
            checksum_algorithm="sha1",
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assertions
        assert result["uuid"] == node_uuid
        assert result["size"] == len(test_content)
        assert result["sha1_checksum"] == expected_sha1
        assert "file_path" in result
        assert "downloaded_at" in result

        # Verify file was created
        output_file = tmp_path / f"{node_uuid}.bin"
        assert output_file.exists()
        assert output_file.read_bytes() == test_content

    def test_download_with_sha256_checksum(self, tmp_path, mock_airflow_context):
        """Test downloading a file with SHA256 checksum calculation."""
        test_content = b"Test content for SHA256"
        expected_sha256 = hashlib.sha256(test_content).hexdigest()
        node_uuid = "test-uuid-456"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            calculate_checksum=True,
            checksum_algorithm="sha256",
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assertions
        assert result["sha256_checksum"] == expected_sha256
        assert "sha1_checksum" not in result

    def test_download_with_md5_checksum(self, tmp_path, mock_airflow_context):
        """Test downloading a file with MD5 checksum calculation."""
        test_content = b"Test content for MD5"
        expected_md5 = hashlib.md5(test_content).hexdigest()
        node_uuid = "test-uuid-789"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            calculate_checksum=True,
            checksum_algorithm="md5",
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assertions
        assert result["md5_checksum"] == expected_md5

    def test_download_without_checksum(self, tmp_path, mock_airflow_context):
        """Test downloading a file without checksum calculation."""
        test_content = b"Test content without checksum"
        node_uuid = "test-uuid-no-checksum"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            calculate_checksum=False,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assertions
        assert result["size"] == len(test_content)
        assert "sha1_checksum" not in result
        assert "sha256_checksum" not in result
        assert "md5_checksum" not in result

    def test_download_with_chunked_streaming(self, tmp_path, mock_airflow_context):
        """Test downloading a file with multiple chunks (streaming)."""
        # Simulate large file with multiple chunks
        chunk1 = b"First chunk of data. "
        chunk2 = b"Second chunk of data. "
        chunk3 = b"Third chunk of data."
        full_content = chunk1 + chunk2 + chunk3
        expected_sha1 = hashlib.sha1(full_content).hexdigest()
        node_uuid = "test-uuid-chunked"

        # Mock HTTP response with multiple chunks
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [chunk1, chunk2, chunk3]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            chunk_size=1024,
            calculate_checksum=True,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assertions
        assert result["size"] == len(full_content)
        assert result["sha1_checksum"] == expected_sha1

        # Verify file contains all chunks
        output_file = tmp_path / f"{node_uuid}.bin"
        assert output_file.read_bytes() == full_content

    def test_download_node_not_found(self, tmp_path, mock_airflow_context):
        """Test download fails when node doesn't exist (404)."""
        node_uuid = "nonexistent-uuid"

        # Mock HTTP 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download", node_id=node_uuid, output_dir=str(tmp_path)
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute and expect exception
        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        assert "not found (404)" in str(exc_info.value)

    def test_download_server_error(self, tmp_path, mock_airflow_context):
        """Test download fails gracefully on server error (500)."""
        node_uuid = "test-uuid-error"

        # Mock HTTP 500 response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download", node_id=node_uuid, output_dir=str(tmp_path)
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute and expect exception
        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        assert "HTTP 500" in str(exc_info.value)

    def test_download_creates_output_directory(self, tmp_path, mock_airflow_context):
        """Test that operator creates output directory if it doesn't exist."""
        test_content = b"Test content"
        node_uuid = "test-uuid-mkdir"

        # Use non-existent nested directory
        nested_dir = tmp_path / "backup_20250110" / "files"
        assert not nested_dir.exists()

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(nested_dir),
            calculate_checksum=False,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Verify directory was created
        assert nested_dir.exists()
        assert (nested_dir / f"{node_uuid}.bin").exists()

    def test_download_cleans_up_on_error(self, tmp_path, mock_airflow_context):
        """Test that partial file is removed if download fails midway."""
        node_uuid = "test-uuid-cleanup"
        output_file = tmp_path / f"{node_uuid}.bin"

        # Mock HTTP response that fails midway
        def failing_iter():
            yield b"Partial content"
            raise ConnectionError("Network error during download")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = failing_iter()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download", node_id=node_uuid, output_dir=str(tmp_path)
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute and expect exception
        with pytest.raises(AirflowException):
            operator.execute(mock_airflow_context)

        # Verify partial file was cleaned up
        assert not output_file.exists()

    def test_invalid_checksum_algorithm(self, tmp_path):
        """Test that invalid checksum algorithm raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            AlfrescoDownloadContentOperator(
                task_id="test_download",
                node_id="test-uuid",
                output_dir=str(tmp_path),
                checksum_algorithm="invalid_algo",
            )

        assert "Invalid checksum_algorithm" in str(exc_info.value)
        assert "Must be one of: sha1, sha256, md5" in str(exc_info.value)

    def test_custom_filename_pattern(self, tmp_path, mock_airflow_context):
        """Test using custom filename pattern."""
        test_content = b"Test content"
        node_uuid = "test-uuid-custom-name"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator with custom filename
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            filename="backup_{uuid}.dat",
            calculate_checksum=False,
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Verify custom filename was used
        expected_file = tmp_path / f"backup_{node_uuid}.dat"
        assert expected_file.exists()
        assert str(expected_file) in result["file_path"]

    def test_http_endpoint_called_correctly(self, tmp_path, mock_airflow_context):
        """Test that correct Alfresco API endpoint is called."""
        test_content = b"Test"
        node_uuid = "workspace-SpacesStore-abc123"

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [test_content]
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        # Create operator
        operator = AlfrescoDownloadContentOperator(
            task_id="test_download",
            node_id=node_uuid,
            output_dir=str(tmp_path),
            http_conn_id="custom_alfresco_conn",
        )

        # Mock http_hook
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        operator.execute(mock_airflow_context)

        # Verify correct endpoint was called
        operator.http_hook.run.assert_called_once()
        call_args = operator.http_hook.run.call_args
        endpoint = call_args[1]["endpoint"]
        assert (
            endpoint
            == f"/alfresco/api/-default-/public/alfresco/versions/1/nodes/{node_uuid}/content"
        )
