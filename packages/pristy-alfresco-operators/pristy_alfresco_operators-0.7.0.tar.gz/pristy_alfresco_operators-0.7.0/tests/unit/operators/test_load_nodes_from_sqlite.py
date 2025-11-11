# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for LoadNodesFromSqliteOperator.
"""

import pytest
import sqlite3
import json
from airflow.exceptions import AirflowException

from pristy.alfresco_operator.load_nodes_from_sqlite import LoadNodesFromSqliteOperator


@pytest.fixture
def populated_sqlite_db(tmp_path):
    """Create a SQLite database populated with test nodes."""
    db_path = tmp_path / "test_backup.db"

    with sqlite3.connect(db_path) as conn:
        # Create schema
        conn.execute("""
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL UNIQUE,
                parent_uuid TEXT,
                node_type TEXT NOT NULL,
                pivot_json TEXT NOT NULL,
                sha1_checksum TEXT,
                file_size INTEGER,
                file_downloaded INTEGER DEFAULT 0,
                state TEXT DEFAULT 'new',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert test nodes
        nodes = [
            # Folders (inserted first, smaller IDs)
            {
                "id": 1,
                "uuid": "folder-1",
                "parent_uuid": None,
                "node_type": "folder",
                "pivot_json": json.dumps(
                    {
                        "name": "Root Folder",
                        "type": "cm:folder",
                        "path": {"root": "site:test", "short": "/"},
                        "source": {"uuid": "folder-1"},
                    }
                ),
                "sha1_checksum": None,
                "file_size": None,
                "file_downloaded": 0,
            },
            {
                "id": 2,
                "uuid": "folder-2",
                "parent_uuid": "folder-1",
                "node_type": "folder",
                "pivot_json": json.dumps(
                    {
                        "name": "Subfolder",
                        "type": "cm:folder",
                        "path": {"root": "site:test", "short": "/Root Folder"},
                        "source": {"uuid": "folder-2"},
                    }
                ),
                "sha1_checksum": None,
                "file_size": None,
                "file_downloaded": 0,
            },
            # Files (inserted later, larger IDs)
            {
                "id": 3,
                "uuid": "file-1",
                "parent_uuid": "folder-1",
                "node_type": "file",
                "pivot_json": json.dumps(
                    {
                        "name": "document1.pdf",
                        "type": "cm:content",
                        "path": {"root": "site:test", "short": "/Root Folder"},
                        "source": {"uuid": "file-1", "size": 1024000},
                    }
                ),
                "sha1_checksum": "abc123",
                "file_size": 1024000,
                "file_downloaded": 1,
            },
            {
                "id": 4,
                "uuid": "file-2",
                "parent_uuid": "folder-2",
                "node_type": "file",
                "pivot_json": json.dumps(
                    {
                        "name": "document2.pdf",
                        "type": "cm:content",
                        "path": {
                            "root": "site:test",
                            "short": "/Root Folder/Subfolder",
                        },
                        "source": {"uuid": "file-2", "size": 2048000},
                    }
                ),
                "sha1_checksum": "def456",
                "file_size": 2048000,
                "file_downloaded": 1,
            },
            {
                "id": 5,
                "uuid": "file-3",
                "parent_uuid": "folder-2",
                "node_type": "file",
                "pivot_json": json.dumps(
                    {
                        "name": "small.txt",
                        "type": "cm:content",
                        "path": {
                            "root": "site:test",
                            "short": "/Root Folder/Subfolder",
                        },
                        "source": {"uuid": "file-3", "size": 1024},
                    }
                ),
                "sha1_checksum": "ghi789",
                "file_size": 1024,
                "file_downloaded": 1,
            },
        ]

        for node in nodes:
            conn.execute(
                """
                INSERT INTO nodes
                (id, uuid, parent_uuid, node_type, pivot_json, sha1_checksum,
                 file_size, file_downloaded, state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'success')
            """,
                (
                    node["id"],
                    node["uuid"],
                    node["parent_uuid"],
                    node["node_type"],
                    node["pivot_json"],
                    node["sha1_checksum"],
                    node["file_size"],
                    node["file_downloaded"],
                ),
            )

        conn.commit()

    return str(db_path)


class TestLoadNodesFromSqliteOperator:
    """Tests for LoadNodesFromSqliteOperator."""

    def test_load_all_nodes(self, populated_sqlite_db, mock_airflow_context):
        """Test loading all nodes without filters."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load", sqlite_path=populated_sqlite_db, batch_size=10
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 5
        # Verify __backup_metadata was added
        assert all("__backup_metadata" in node for node in result)
        assert result[0]["__backup_metadata"]["original_uuid"] == "folder-1"

    def test_load_folders_only(self, populated_sqlite_db, mock_airflow_context):
        """Test loading only folder nodes."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load",
            sqlite_path=populated_sqlite_db,
            batch_size=10,
            node_type_filter="folder",
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 2
        assert all(node["type"] == "cm:folder" for node in result)
        assert result[0]["name"] == "Root Folder"
        assert result[1]["name"] == "Subfolder"

    def test_load_files_only(self, populated_sqlite_db, mock_airflow_context):
        """Test loading only file nodes."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load",
            sqlite_path=populated_sqlite_db,
            batch_size=10,
            node_type_filter="file",
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 3
        assert all(node["type"] == "cm:content" for node in result)

    def test_batch_size_limit(self, populated_sqlite_db, mock_airflow_context):
        """Test that batch_size limits the number of results."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load", sqlite_path=populated_sqlite_db, batch_size=2
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 2

    def test_pagination_with_offset(self, populated_sqlite_db, mock_airflow_context):
        """Test pagination using offset parameter."""
        # First batch
        operator1 = LoadNodesFromSqliteOperator(
            task_id="test_load_1",
            sqlite_path=populated_sqlite_db,
            batch_size=2,
            offset=0,
        )
        result1 = operator1.execute(mock_airflow_context)

        # Second batch
        operator2 = LoadNodesFromSqliteOperator(
            task_id="test_load_2",
            sqlite_path=populated_sqlite_db,
            batch_size=2,
            offset=2,
        )
        result2 = operator2.execute(mock_airflow_context)

        # Should get different nodes
        assert len(result1) == 2
        assert len(result2) == 2
        assert (
            result1[0]["__backup_metadata"]["original_uuid"]
            != result2[0]["__backup_metadata"]["original_uuid"]
        )

    def test_custom_order_by(self, populated_sqlite_db, mock_airflow_context):
        """Test custom ORDER BY clause."""
        # Order files by size descending
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load",
            sqlite_path=populated_sqlite_db,
            batch_size=10,
            node_type_filter="file",
            order_by="file_size DESC",
        )

        result = operator.execute(mock_airflow_context)

        # Should get files ordered by size (largest first)
        assert len(result) == 3
        assert result[0]["__backup_metadata"]["file_size"] == 2048000  # largest
        assert result[1]["__backup_metadata"]["file_size"] == 1024000
        assert result[2]["__backup_metadata"]["file_size"] == 1024  # smallest

    def test_backup_metadata_contains_all_fields(
        self, populated_sqlite_db, mock_airflow_context
    ):
        """Test that __backup_metadata contains all expected fields."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load",
            sqlite_path=populated_sqlite_db,
            batch_size=1,
            node_type_filter="file",
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 1
        backup_meta = result[0]["__backup_metadata"]

        assert "original_uuid" in backup_meta
        assert "parent_uuid" in backup_meta
        assert "sha1_checksum" in backup_meta
        assert "file_size" in backup_meta
        assert "file_downloaded" in backup_meta

        assert backup_meta["sha1_checksum"] == "abc123"
        assert backup_meta["file_size"] == 1024000
        assert backup_meta["file_downloaded"] is True

    def test_database_not_found(self, tmp_path, mock_airflow_context):
        """Test that missing database raises exception."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load",
            sqlite_path=str(tmp_path / "nonexistent.db"),
            batch_size=10,
        )

        with pytest.raises(AirflowException) as exc_info:
            operator.execute(mock_airflow_context)

        assert "not found" in str(exc_info.value)

    def test_invalid_node_type_filter(self):
        """Test that invalid node_type_filter raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            LoadNodesFromSqliteOperator(
                task_id="test_load",
                sqlite_path="/tmp/test.db",
                node_type_filter="invalid_type",
            )

        assert "Invalid node_type_filter" in str(exc_info.value)

    def test_readonly_mode(self, populated_sqlite_db, mock_airflow_context):
        """Test that database is opened in read-only mode."""
        operator = LoadNodesFromSqliteOperator(
            task_id="test_load", sqlite_path=populated_sqlite_db, batch_size=10
        )

        # This should succeed (read operation)
        result = operator.execute(mock_airflow_context)
        assert len(result) > 0

        # Verify database wasn't modified by checking row count
        with sqlite3.connect(populated_sqlite_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM nodes")
            count = cursor.fetchone()[0]
            assert count == 5  # Should still have original 5 nodes

    def test_empty_database(self, tmp_path, mock_airflow_context):
        """Test loading from empty database returns empty list."""
        db_path = tmp_path / "empty.db"

        # Create empty database with schema
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY,
                    uuid TEXT NOT NULL,
                    parent_uuid TEXT,
                    node_type TEXT NOT NULL,
                    pivot_json TEXT NOT NULL,
                    sha1_checksum TEXT,
                    file_size INTEGER,
                    file_downloaded INTEGER DEFAULT 0,
                    state TEXT DEFAULT 'new'
                )
            """)

        operator = LoadNodesFromSqliteOperator(
            task_id="test_load", sqlite_path=str(db_path), batch_size=10
        )

        result = operator.execute(mock_airflow_context)
        assert result == []

    def test_special_characters_preserved(self, tmp_path, mock_airflow_context):
        """Test that special characters in node data are preserved."""
        db_path = tmp_path / "special.db"

        # Create database with special characters
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE nodes (
                    id INTEGER PRIMARY KEY,
                    uuid TEXT NOT NULL,
                    parent_uuid TEXT,
                    node_type TEXT NOT NULL,
                    pivot_json TEXT NOT NULL,
                    sha1_checksum TEXT,
                    file_size INTEGER,
                    file_downloaded INTEGER DEFAULT 0,
                    state TEXT DEFAULT 'new'
                )
            """)

            special_node = {
                "name": "Dossier éàç ñ ü.pdf",
                "type": "cm:content",
                "properties": {"cm:title": "Caractères spéciaux: àéèù ñ ü 🚀"},
                "source": {"uuid": "special-123"},
            }

            conn.execute(
                """
                INSERT INTO nodes (uuid, parent_uuid, node_type, pivot_json, file_size, file_downloaded)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    "special-123",
                    None,
                    "file",
                    json.dumps(special_node, ensure_ascii=False),
                    1024,
                    1,
                ),
            )
            conn.commit()

        operator = LoadNodesFromSqliteOperator(
            task_id="test_load", sqlite_path=str(db_path), batch_size=10
        )

        result = operator.execute(mock_airflow_context)

        assert len(result) == 1
        assert result[0]["name"] == "Dossier éàç ñ ü.pdf"
        assert result[0]["properties"]["cm:title"] == "Caractères spéciaux: àéèù ñ ü 🚀"
