from __future__ import annotations

from .core.http import HttpClient

class Settings:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /settings/{projectID}
    def get(self, project_id: str):
        return self.http.request("GET", f"/settings/{project_id}")
