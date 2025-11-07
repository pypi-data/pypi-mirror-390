from __future__ import annotations
from typing import Any, Dict, Optional

from .core.http import HttpClient

class Tasks:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /tasks/?projectID=...&limit=...&skip=...&created_by=...
    def list(self, project_id: str, *, limit: Optional[int] = None, skip: Optional[int] = None, created_by: Optional[str] = None):
        params: Dict[str, Any] = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        if skip is not None:
            params["skip"] = skip
        if created_by:
            params["created_by"] = created_by
        return self.http.request("GET", "/tasks/", params=params)

    # GET /task/{id}?projectID=...
    def get(self, task_id: str, project_id: Optional[str] = None):
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/task/{task_id}", params=params)

    # POST /task/{id}/pause
    def pause(self, task_id: str):
        return self.http.request("POST", f"/task/{task_id}/pause")

    # POST /task/{id}/resume
    def resume(self, task_id: str):
        return self.http.request("POST", f"/task/{task_id}/resume")

    # POST /task/{id}/stop
    def stop(self, task_id: str):
        return self.http.request("POST", f"/task/{task_id}/stop")
