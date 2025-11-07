from __future__ import annotations
from typing import Any

from .core.http import HttpClient

class Analytics:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /analytics?projectID=...
    def get(self, project_id: str) -> Any:
        return self.http.request("GET", "/analytics", params={"projectID": project_id})
