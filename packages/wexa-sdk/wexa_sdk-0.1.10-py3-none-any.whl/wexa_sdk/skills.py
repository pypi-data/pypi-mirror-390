from __future__ import annotations
from typing import Optional, TypedDict, Dict, Any

from .core.http import HttpClient


class SkillCreateBody(TypedDict):
    """Body for creating a Skill.

    Required (user_id can be null but key is required):
      - name: str
      - logo: str
      - connector_name: str
      - description: str
      - projectID: str
      - connector_id: str
      - user_id: Optional[str]
    """
    name: str
    logo: str
    connector_name: str
    description: str
    projectID: str
    connector_id: str
    user_id: Optional[str]


class Skills:
    def __init__(self, http: HttpClient):
        self.http = http

    # POST /skills/
    def create(self, body: SkillCreateBody):
        return self.http.request("POST", "/skills/", json=body)

    # GET /skills/?projectID=...&limit=...
    def list(self, project_id: str, *, limit: Optional[int] = None):
        params = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        return self.http.request("GET", "/skills/", params=params)

    # GET /skills/category?projectId=...&category=...&limit=...
    def list_by_category(self, project_id: str, category: str, *, limit: Optional[int] = None):
        params: Dict[str, Any] = {"projectId": project_id, "category": category}
        if limit is not None:
            params["limit"] = limit
        return self.http.request("GET", "/skills/category", params=params)

    # GET /skills/{id}
    def get_by_id(self, skill_id: str):
        return self.http.request("GET", f"/skills/{skill_id}")

    # GET /skills/?name=...&projectID=...
    def get_by_name(self, name: str, project_id: str):
        params = {"name": name, "projectID": project_id}
        return self.http.request("GET", "/skills/", params=params)
