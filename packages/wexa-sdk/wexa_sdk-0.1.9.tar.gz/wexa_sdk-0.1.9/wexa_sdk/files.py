from __future__ import annotations
from typing import Any, Dict, Optional, TypedDict

from .core.http import HttpClient

class Files:
    def __init__(self, http: HttpClient):
        self.http = http

    # POST /files/upload?projectID=...&container_name=...
    # body example: { "filenames": ["file.pdf"], "tags": ["resume"], "source_type": "STORAGE", "org_id": "..." }
    class UploadFilesBody(TypedDict):
        filenames: list[str]
        tags: list[str]
        projectID: str
        source_type: str
        org_id: str

    def upload_request(self, project_id: str, container_name: str, body: UploadFilesBody):
        params: Dict[str, Any] = {"projectID": project_id, "container_name": container_name}
        return self.http.request("POST", "/files/upload", params=params, json=body)

    # GET /file/{fileId}/?projectID=...
    def get_by_file_id(self, file_id: str, project_id: Optional[str] = None):
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/file/{file_id}/", params=params)

    # GET /files/{connectorId}/connector/
    def list_by_connector(self, connector_id: str):
        return self.http.request("GET", f"/files/{connector_id}/connector/")
