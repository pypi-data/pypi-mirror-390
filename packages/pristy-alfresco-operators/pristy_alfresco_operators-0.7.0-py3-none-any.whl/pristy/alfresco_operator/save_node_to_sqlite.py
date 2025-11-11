# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Dict, Any, Optional

from airflow.models.baseoperator import BaseOperator


class SaveNodeToSqliteOperator(BaseOperator):
    """
    Saves Alfresco node metadata to a SQLite database for backup purposes.

    This operator stores nodes in Pristy pivot format as JSON strings in a SQLite
    database, along with checksum information for file integrity verification.

    The SQLite database must have the following schema (created by backup init DAG):
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            parent_uuid TEXT,
            node_type TEXT NOT NULL,  -- 'folder' or 'file'
            pivot_json TEXT NOT NULL, -- Complete Pristy pivot format as JSON
            sha1_checksum TEXT,       -- SHA1 hash of binary content (NULL for folders)
            file_size INTEGER,        -- File size in bytes (NULL for folders)
            file_downloaded INTEGER DEFAULT 0,  -- 1 if binary downloaded
            state TEXT DEFAULT 'new',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

    :param nodes: (required) List of nodes in Pristy pivot format to save
    :param sqlite_path: (required) Path to SQLite database file
    :param file_downloaded: Flag indicating if binary content was downloaded (default: False)
    :param checksums: Optional dict mapping node UUID to SHA1 checksum

    :returns: Dictionary with:
        - saved_count: Number of nodes saved
        - skipped_count: Number of nodes skipped (already exist)

    Example usage:
        save_task = SaveNodeToSqliteOperator(
            task_id="save_metadata",
            nodes=[
                {
                    "name": "document.pdf",
                    "type": "cm:content",
                    "path": {"root": "site:my-site", "short": "/folder1"},
                    "properties": {"cm:title": "My Document"},
                    "source": {
                        "uuid": "workspace://SpacesStore/abc123",
                        "size": 1024000
                    },
                    "__dag_param": {"parent_uuid": "workspace://SpacesStore/parent123"}
                }
            ],
            sqlite_path="/datas/backups/backup_20250110/backup.db",
            file_downloaded=True,
            checksums={"workspace://SpacesStore/abc123": "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"}
        )
    """

    def __init__(
        self,
        *,
        nodes: List[Dict[str, Any]],
        sqlite_path: str,
        file_downloaded: bool = False,
        checksums: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.nodes = nodes
        self.sqlite_path = sqlite_path
        self.file_downloaded = file_downloaded
        self.checksums = checksums or {}

    def execute(self, context):
        # Lazy imports
        import sqlite3
        import json
        from datetime import datetime, timezone
        from airflow.exceptions import AirflowException

        if not self.nodes:
            self.log.info("No nodes to save")
            return {"saved_count": 0, "skipped_count": 0}

        self.log.info(
            f"Saving {len(self.nodes)} nodes to SQLite database: {self.sqlite_path}"
        )

        saved_count = 0
        skipped_count = 0

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                for node in self.nodes:
                    # Extract node information
                    source = node.get("source", {})
                    uuid = source.get("uuid")

                    if not uuid:
                        self.log.warning(
                            f"Node missing source.uuid, skipping: {node.get('name', 'unknown')}"
                        )
                        skipped_count += 1
                        continue

                    # Extract parent UUID from DAG parameters
                    parent_uuid = node.get("__dag_param", {}).get("parent_uuid")

                    # Determine node type
                    node_type_value = node.get("type", "")
                    if node_type_value == "cm:content":
                        node_type = "file"
                    elif node_type_value in ("cm:folder", ""):
                        node_type = "folder"
                    else:
                        # Assume it's a file if it has content
                        node_type = "file" if "source" in node else "folder"

                    # Extract file information
                    file_size = source.get("size")
                    sha1_checksum = self.checksums.get(uuid)

                    # Serialize node to JSON
                    pivot_json = json.dumps(node, ensure_ascii=False)

                    # Get current timestamp
                    now = datetime.now(timezone.utc).isoformat()

                    # Check if node already exists
                    cursor.execute(
                        "SELECT id FROM nodes WHERE uuid = ?",
                        (uuid,),
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing node
                        cursor.execute(
                            """
                            UPDATE nodes
                            SET parent_uuid = ?,
                                node_type = ?,
                                pivot_json = ?,
                                sha1_checksum = ?,
                                file_size = ?,
                                file_downloaded = ?,
                                state = 'success',
                                updated_at = ?
                            WHERE uuid = ?
                        """,
                            (
                                parent_uuid,
                                node_type,
                                pivot_json,
                                sha1_checksum,
                                file_size,
                                1 if self.file_downloaded else 0,
                                now,
                                uuid,
                            ),
                        )
                        self.log.debug(f"Updated existing node: {uuid}")
                    else:
                        # Insert new node
                        cursor.execute(
                            """
                            INSERT INTO nodes
                            (uuid, parent_uuid, node_type, pivot_json, sha1_checksum,
                             file_size, file_downloaded, state, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'success', ?, ?)
                        """,
                            (
                                uuid,
                                parent_uuid,
                                node_type,
                                pivot_json,
                                sha1_checksum,
                                file_size,
                                1 if self.file_downloaded else 0,
                                now,
                                now,
                            ),
                        )
                        self.log.debug(f"Inserted new node: {uuid}")

                    saved_count += 1

                # Commit transaction
                conn.commit()

            self.log.info(
                f"Successfully saved {saved_count} nodes "
                f"({skipped_count} skipped without UUID)"
            )

            return {"saved_count": saved_count, "skipped_count": skipped_count}

        except sqlite3.Error as e:
            raise AirflowException(f"SQLite error: {str(e)}") from e
        except Exception as e:
            raise AirflowException(f"Failed to save nodes to SQLite: {str(e)}") from e
