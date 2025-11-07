from __future__ import annotations
from typing import Any, Dict, Optional

from .core.http import HttpClient

class Inbox:
    def __init__(self, http: HttpClient):
        self.http = http

    # POST /inbox/create
    def create(self, body: Dict[str, Any]):
        return self.http.request("POST", "/inbox/create", json=body)

    # GET /inbox?projectID=...&limit=...
    def list(self, project_id: str, *, limit: Optional[int] = None):
        params: Dict[str, Any] = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        return self.http.request("GET", "/inbox", params=params)

    # POST /inbox/update/runtime_input/?projectID=...
    def update_runtime(self, project_id: str, body: Dict[str, Any]):
        return self.http.request("POST", "/inbox/update/runtime_input/", params={"projectID": project_id}, json=body)

    # POST /inbox/update/anomaly_detection/?projectID=...
    def update_anomaly(self, project_id: str, body: Dict[str, Any]):
        return self.http.request("POST", "/inbox/update/anomaly_detection/", params={"projectID": project_id}, json=body)

    # POST /inbox/update/preview/?projectID=...
    def update_preview(self, project_id: str, body: Dict[str, Any]):
        return self.http.request("POST", "/inbox/update/preview/", params={"projectID": project_id}, json=body)

    # POST /inbox/update/preview/{execution_id}?projectID=...
    def update_preview_by_execution(self, execution_id: str, body: Dict[str, Any], project_id: Optional[str] = None):
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/preview/{execution_id}", params=params, json=body)

    # GET /inbox/{id}?projectID=...
    def get(self, inbox_id: str, project_id: Optional[str] = None):
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/inbox/{inbox_id}", params=params)
