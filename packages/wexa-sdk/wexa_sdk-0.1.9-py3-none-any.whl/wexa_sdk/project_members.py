from __future__ import annotations
from typing import Any

from .core.http import HttpClient

class ProjectMembers:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /project-member/{projectID}/summary
    def summary(self, project_id: str) -> Any:
        return self.http.request("GET", f"/project-member/{project_id}/summary")

    # GET /project-member/{projectID}
    def list(self, project_id: str) -> Any:
        return self.http.request("GET", f"/project-member/{project_id}")
