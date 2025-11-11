# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0


from typing import Dict, Any, Optional

from airflow.models.baseoperator import BaseOperator
from airflow.providers.http.hooks.http import HttpHook


class AlfrescoUploadPristyOperator(BaseOperator):
    """
    Uploads files and folders to Alfresco using the custom Pristy injector endpoint.

    This operator uses the Pristy custom REST API that supports multipart/form-data uploads
    with automatic folder hierarchy creation and rich metadata injection.

    The endpoint accepts:
    - `file`: Binary file content (optional, for file nodes only)
    - `fileSize`: File size in bytes as string (required if file provided)
    - `metadata`: JSON string containing Pristy pivot format WITHOUT the 'source' field

    Features:
    - Automatic folder hierarchy creation from path
    - Supports both file and folder creation
    - Rich metadata support (properties, aspects, permissions)
    - Idempotent: overwrites existing nodes with same path+name

    :param file_path: (optional) Path to binary file to upload. If None, creates folder only.
    :param metadata: (required) Dictionary containing Pristy pivot format WITHOUT 'source' field.
        Must include: name, path (with root and short/full), and optional properties, permissions, etc.
    :param http_conn_id: Airflow connection ID for Alfresco HTTP API (default: "alfresco_api")
    :param endpoint: Custom Pristy endpoint path (default: "/alfresco/service/fr/jeci/pristy/nodes/inject")

    :returns: Dictionary containing:
        - node: Full node reference (e.g., "workspace://SpacesStore/uuid")
        - displayPath: Human-readable path in Alfresco

    Example metadata for file upload:
        {
            "name": "document.pdf",
            "type": "cm:content",
            "owner": "admin",
            "createdAt": "2024-01-15T10:30:00.000Z",
            "path": {
                "root": "site:pristy-mdph",
                "short": "/12/12345678/Dossier MDPH"
            },
            "properties": {
                "cm:title": "Dossier MDPH",
                "sm:infosBeneficiaire": "12345678"
            },
            "permissions": {
                "inherited": false,
                "locallySet": [
                    {"authorityId": "GROUP_site_pristy-mdph_SiteManager", "name": "SiteManager"}
                ]
            }
        }

    Example usage:
        # Upload file
        upload_file = AlfrescoUploadPristyOperator(
            task_id="upload_document",
            file_path="/datas/backups/backup_20250110/files/uuid123.bin",
            metadata={
                "name": "document.pdf",
                "path": {"root": "site:my-site", "short": "/folder1/folder2"},
                "properties": {"cm:title": "My Document"}
            }
        )

        # Create folder only
        create_folder = AlfrescoUploadPristyOperator(
            task_id="create_folder",
            file_path=None,
            metadata={
                "name": "New Folder",
                "type": "cm:folder",
                "path": {"root": "site:my-site", "short": "/parent"},
                "properties": {"cm:title": "My Folder"}
            }
        )
    """

    def __init__(
        self,
        *,
        file_path: Optional[str] = None,
        metadata: Dict[str, Any],
        http_conn_id: str = "alfresco_api",
        endpoint: str = "/alfresco/service/fr/jeci/pristy/nodes/inject",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.metadata = metadata
        self.http_conn_id = http_conn_id
        self.endpoint = endpoint

        # Validate metadata
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
        if "name" not in self.metadata:
            raise ValueError("metadata must contain 'name' field")
        if "path" not in self.metadata:
            raise ValueError("metadata must contain 'path' field")
        if "source" in self.metadata:
            self.log.warning(
                "'source' field found in metadata. This will be ignored by the Pristy endpoint. "
                "The endpoint expects metadata WITHOUT the 'source' field."
            )

    def execute(self, context):
        # Lazy imports to avoid loading heavy dependencies at DAG parse time
        import json
        from pathlib import Path
        from airflow.exceptions import AirflowException

        self.log.info(f"Uploading to Pristy endpoint: {self.endpoint}")

        # Prepare multipart form data
        files = {}
        data = {}

        if self.file_path:
            # File upload mode
            file_obj = Path(self.file_path)
            if not file_obj.exists():
                raise AirflowException(f"File not found: {self.file_path}")

            file_size = file_obj.stat().st_size
            self.log.info(f"Uploading file: {file_obj.name} ({file_size} bytes)")

            # Open file for multipart upload
            # Note: The file will be closed by requests library after upload
            files = {
                "file": (
                    file_obj.name,
                    open(self.file_path, "rb"),
                    "application/octet-stream",
                )
            }

            data = {
                "fileSize": str(file_size),
                "metadata": json.dumps(self.metadata, ensure_ascii=False),
            }
        else:
            # Folder creation mode (no file)
            self.log.info(f"Creating folder: {self.metadata.get('name')}")
            data = {"metadata": json.dumps(self.metadata, ensure_ascii=False)}

        # Create HTTP hook
        http_hook = HttpHook(method="POST", http_conn_id=self.http_conn_id)

        try:
            # Make multipart/form-data request
            # IMPORTANT: Do NOT set Content-Type header - requests library will set it
            # automatically with the correct boundary
            response = http_hook.run(
                endpoint=self.endpoint,
                data=data,
                files=files if files else None,
                extra_options={"check_response": False},
                headers={"Accept": "application/json"},
            )

            # Check response status
            if response.status_code == 200:
                result = response.json()
                self.log.info(
                    f"Successfully uploaded to Alfresco: {result.get('node')} "
                    f"at path {result.get('displayPath')}"
                )
                return result
            else:
                # Try to parse error message
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", response.text)
                except:
                    error_msg = response.text

                raise AirflowException(
                    f"Failed to upload to Pristy endpoint: HTTP {response.status_code} - {error_msg}"
                )

        except Exception as e:
            raise AirflowException(f"Failed to upload to Alfresco: {str(e)}") from e

        finally:
            # Close file handles if opened
            if files and "file" in files:
                try:
                    files["file"][1].close()
                except:
                    pass
