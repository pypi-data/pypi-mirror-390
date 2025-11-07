from __future__ import annotations
from typing import Optional, Dict, Any, TypedDict
from urllib.parse import quote

from .core.http import HttpClient


class ProjectCreateBody(TypedDict, total=False):
    """Body for creating a project.

    Required fields:
      - orgId: str
      - projectName: str

    Optional fields:
      - description: str
      - coworker_role: str
      - status: str (e.g., "published")
    """
    orgId: str
    projectName: str
    description: str
    coworker_role: str
    status: str

class Projects:
    def __init__(self, http: HttpClient):
        self.http = http

    # Per developers.wexa.ai: POST https://api.wexa.ai/v1/project
    def create(self, body: ProjectCreateBody):
        """
        Create a project with a request body.

        Example body:
        {
          "orgId": "67fdea40aac77be632954f0f",
          "projectName": "New",
          "description": "yoooo",
          "coworker_role": "testrole",
          "status": "published"
        }
        """
        return self.http.request("POST", "/v1/project", json=body)

    def create_simple(
        self,
        *,
        orgId: str,
        projectName: str,
        description: Optional[str] = None,
        coworker_role: Optional[str] = None,
        status: Optional[str] = None,
    ):
        """Convenience wrapper: builds the body and calls create(body)."""
        body: Dict[str, Any] = {"orgId": orgId, "projectName": projectName}
        if description is not None:
            body["description"] = description
        if coworker_role is not None:
            body["coworker_role"] = coworker_role
        if status is not None:
            body["status"] = status
        return self.create(body)  # type: ignore[arg-type]

    def list(self):
        return self.http.request("GET", "/v1/project")

    def list_all(self, user_id: str):
        """
        Get all projects for a given user (organization-wide).
        GET /v1/project/all?userId=...

        Headers:
          - x-api-key: string (required)

        Query params:
          - userId: string (required)
        """
        params = {"userId": user_id}
        return self.http.request("GET", "/v1/project/all", params=params)

    def get_all(
        self,
        *,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        Get all projects with optional filters and pagination.
        GET /v1/project?status=...&userId=...&orgId=...&page=...&limit=...

        Args:
            status: Optional project status filter (e.g., "published").
            user_id: Optional user filter.
            org_id: Optional organization filter.
            page: Optional page number (int).
            limit: Optional page size (int).
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if user_id is not None:
            params["userId"] = user_id
        if org_id is not None:
            params["orgId"] = org_id
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        return self.http.request("GET", "/v1/project", params=params)

    def get(self, project_id: str):
        return self.http.request("GET", f"/v1/project/{project_id}")

    class ProjectUpdateBody(TypedDict):
        orgId: str
        projectName: str
        description: str
        coworker_role: str

    def update(self, project_id: str, body: ProjectUpdateBody):
        """Update a project via PUT /v1/project?projectId=... with required fields.

        Required body keys: orgId, projectName, description, coworker_role
        """
        params = {"projectId": project_id}
        return self.http.request("PUT", "/v1/project", params=params, json=body)

    def delete(self, project_id: str):
        return self.http.request("DELETE", f"/v1/project/{project_id}")

    def get_by_project_name(self, project_name: str):
        """
        Get project by projectName.

        GET /project/projectName/{projectName}
        """
        safe = quote(project_name, safe="")
        return self.http.request("GET", f"/project/projectName/{safe}")
