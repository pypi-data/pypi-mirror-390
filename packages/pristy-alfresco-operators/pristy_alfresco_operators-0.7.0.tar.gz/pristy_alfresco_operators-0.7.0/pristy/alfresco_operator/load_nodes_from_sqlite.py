# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from airflow.models.baseoperator import BaseOperator


class LoadNodesFromSqliteOperator(BaseOperator):
    """
    Loads node metadata from a SQLite backup database for restoration.

    This operator reads nodes stored in Pristy pivot format from a SQLite database
    created during backup. The database is opened in READ-ONLY mode to prevent
    accidental modification of the backup.

    The operator supports pagination, filtering by node type, and ordering to process
    nodes in the correct sequence (e.g., folders before files, parents before children).

    :param sqlite_path: (required) Path to SQLite database file (read-only)
    :param batch_size: Number of nodes to load per execution (default: 10)
    :param node_type_filter: Filter by node type: 'folder' or 'file' (default: None = all types)
    :param state_filter: Filter by state (default: 'new'). Note: This is for future use
        as the backup SQLite is read-only during restore.
    :param order_by: SQL ORDER BY clause (default: 'id ASC' to process in insertion order)
    :param offset: Skip first N records (default: 0, for pagination)

    :returns: List of dictionaries, each containing:
        - All fields from the Pristy pivot JSON
        - __backup_metadata: Dict with original_uuid, sha1_checksum, file_size from backup

    Example usage:
        # Load folders in order (parents before children)
        load_folders = LoadNodesFromSqliteOperator(
            task_id="load_folders",
            sqlite_path="/datas/backups/backup_20250110/backup.db",
            batch_size=10,
            node_type_filter='folder',
            order_by='id ASC'
        )

        # Load files with pagination
        load_files = LoadNodesFromSqliteOperator(
            task_id="load_files_batch",
            sqlite_path="/datas/backups/backup_20250110/backup.db",
            batch_size=20,
            node_type_filter='file',
            order_by='file_size DESC'  # Process largest files first
        )
    """

    def __init__(
        self,
        *,
        sqlite_path: str,
        batch_size: int = 10,
        node_type_filter: Optional[str] = None,
        state_filter: str = "new",
        order_by: str = "id ASC",
        offset: int = 0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.sqlite_path = sqlite_path
        self.batch_size = batch_size
        self.node_type_filter = node_type_filter
        self.state_filter = state_filter
        self.order_by = order_by
        self.offset = offset

        # Validate node_type_filter
        if self.node_type_filter and self.node_type_filter not in ("folder", "file"):
            raise ValueError(
                f"Invalid node_type_filter: {self.node_type_filter}. "
                "Must be 'folder', 'file', or None"
            )

    def execute(self, context):
        # Lazy imports
        import sqlite3
        import json
        from pathlib import Path
        from airflow.exceptions import AirflowException

        # Verify database exists
        db_path = Path(self.sqlite_path)
        if not db_path.exists():
            raise AirflowException(f"SQLite database not found: {self.sqlite_path}")

        self.log.info(
            f"Loading nodes from SQLite database: {self.sqlite_path} "
            f"(batch_size={self.batch_size}, filter={self.node_type_filter})"
        )

        nodes = []

        try:
            # Open database in READ-ONLY mode (important for backup integrity)
            # URI format: file:path?mode=ro
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row  # Access columns by name

            try:
                cursor = conn.cursor()

                # Build query with filters
                query = """
                    SELECT uuid, parent_uuid, node_type, pivot_json,
                           sha1_checksum, file_size, file_downloaded
                    FROM nodes
                    WHERE 1=1
                """
                params = []

                if self.node_type_filter:
                    query += " AND node_type = ?"
                    params.append(self.node_type_filter)

                # Note: state_filter is included for API compatibility but not used
                # since backup SQLite is read-only. Could be used in future if needed.

                # Add ordering and pagination
                query += f" ORDER BY {self.order_by}"
                query += " LIMIT ? OFFSET ?"
                params.extend([self.batch_size, self.offset])

                # Execute query
                cursor.execute(query, params)
                rows = cursor.fetchall()

                self.log.info(f"Found {len(rows)} nodes matching criteria")

                # Parse each row
                for row in rows:
                    try:
                        # Parse the pivot JSON
                        node_data = json.loads(row["pivot_json"])

                        # Add backup metadata for restore operations
                        node_data["__backup_metadata"] = {
                            "original_uuid": row["uuid"],
                            "parent_uuid": row["parent_uuid"],
                            "sha1_checksum": row["sha1_checksum"],
                            "file_size": row["file_size"],
                            "file_downloaded": bool(row["file_downloaded"]),
                        }

                        nodes.append(node_data)

                    except json.JSONDecodeError as e:
                        self.log.error(
                            f"Failed to parse pivot_json for node {row['uuid']}: {e}"
                        )
                        continue

                self.log.info(
                    f"Successfully loaded {len(nodes)} nodes from SQLite backup"
                )

                return nodes

            finally:
                conn.close()

        except sqlite3.Error as e:
            raise AirflowException(f"SQLite error: {str(e)}") from e
        except Exception as e:
            raise AirflowException(f"Failed to load nodes from SQLite: {str(e)}") from e
