# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from airflow.models.baseoperator import BaseOperator
from airflow.providers.http.hooks.http import HttpHook


class AlfrescoDownloadContentOperator(BaseOperator):
    """
    Downloads binary content from an Alfresco node to the local filesystem.

    This operator streams the file content to avoid memory issues with large files,
    and optionally calculates a checksum (SHA1, SHA256, MD5) during the download.

    :param node_id: (required) UUID of the Alfresco node to download
    :param output_dir: (required) Directory where the file will be saved
    :param filename: Filename pattern (default: "{uuid}.bin"). Use {uuid} placeholder.
    :param http_conn_id: Airflow connection ID for Alfresco HTTP API (default: "alfresco_api")
    :param chunk_size: Size of chunks for streaming download in bytes (default: 8192)
    :param calculate_checksum: Whether to calculate file checksum (default: True)
    :param checksum_algorithm: Hash algorithm to use: "sha1", "sha256", or "md5" (default: "sha1")

    :returns: Dictionary containing:
        - file_path: Absolute path to downloaded file
        - size: File size in bytes
        - uuid: Node UUID
        - sha1_checksum / sha256_checksum / md5_checksum: Hex digest (if calculate_checksum=True)
        - downloaded_at: ISO 8601 timestamp

    Example usage:
        download_task = AlfrescoDownloadContentOperator(
            task_id="download_file",
            node_id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
            output_dir="/datas/backups/backup_20250110/files",
            filename="{uuid}.bin",
            calculate_checksum=True,
            checksum_algorithm="sha1"
        )
    """

    def __init__(
        self,
        *,
        node_id: str,
        output_dir: str,
        filename: str = "{uuid}.bin",
        http_conn_id: str = "alfresco_api",
        chunk_size: int = 8192,
        calculate_checksum: bool = True,
        checksum_algorithm: str = "sha1",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.alf_node_id = node_id
        self.output_dir = output_dir
        self.filename = filename
        self.chunk_size = chunk_size
        self.calculate_checksum = calculate_checksum
        self.checksum_algorithm = checksum_algorithm.lower()
        self.http_hook = HttpHook(method="GET", http_conn_id=http_conn_id)

        # Validate checksum algorithm
        if self.checksum_algorithm not in ("sha1", "sha256", "md5"):
            raise ValueError(
                f"Invalid checksum_algorithm: {self.checksum_algorithm}. "
                "Must be one of: sha1, sha256, md5"
            )

    def execute(self, context):
        # Lazy imports to avoid loading heavy dependencies at DAG parse time
        import hashlib
        from datetime import datetime, timezone
        from pathlib import Path
        from airflow.exceptions import AirflowException

        # Resolve node_id if it's a template
        node_id_resolved = str(self.alf_node_id)
        if hasattr(self.alf_node_id, "resolve"):
            node_id_resolved = self.alf_node_id.resolve(context)

        # Prepare output path
        output_path = Path(self.output_dir) / self.filename.format(
            uuid=node_id_resolved
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.log.info(
            f"Downloading content from node {node_id_resolved} to {output_path}"
        )

        # Initialize hash calculator if requested
        hash_calculator: Optional[hashlib._hashlib.HASH] = None
        if self.calculate_checksum:
            if self.checksum_algorithm == "sha1":
                hash_calculator = hashlib.sha1()
            elif self.checksum_algorithm == "sha256":
                hash_calculator = hashlib.sha256()
            elif self.checksum_algorithm == "md5":
                hash_calculator = hashlib.md5()

        file_size = 0

        try:
            # Stream download with checksum calculation
            endpoint = f"/alfresco/api/-default-/public/alfresco/versions/1/nodes/{node_id_resolved}/content"

            with self.http_hook.run(
                endpoint=endpoint,
                extra_options={"stream": True, "check_response": False},
            ) as response:
                # Check response status
                if response.status_code == 404:
                    raise AirflowException(f"Node {node_id_resolved} not found (404)")
                elif response.status_code != 200:
                    raise AirflowException(
                        f"Failed to download node {node_id_resolved}: "
                        f"HTTP {response.status_code} - {response.text}"
                    )

                # Stream content to file and calculate checksum
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)
                            file_size += len(chunk)
                            if hash_calculator:
                                hash_calculator.update(chunk)

            # Build result dictionary
            result = {
                "file_path": str(output_path.absolute()),
                "size": file_size,
                "uuid": node_id_resolved,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }

            # Add checksum if calculated
            if hash_calculator:
                checksum_key = f"{self.checksum_algorithm}_checksum"
                result[checksum_key] = hash_calculator.hexdigest()
                self.log.info(
                    f"Downloaded {file_size} bytes with {self.checksum_algorithm.upper()} "
                    f"checksum: {result[checksum_key]}"
                )
            else:
                self.log.info(f"Downloaded {file_size} bytes (no checksum calculated)")

            return result

        except Exception as e:
            # Clean up partial file on error
            if output_path.exists():
                self.log.warning(f"Removing partial file: {output_path}")
                output_path.unlink()
            raise AirflowException(
                f"Failed to download node {node_id_resolved}: {str(e)}"
            ) from e
