from __future__ import annotations
from typing import Any, Optional, TypedDict

from ..core.http import HttpClient
from .google_drive import GoogleDrive

class ConnectorConfigBody(TypedDict, total=False):
    """JSON body for configuring a connector via POST /actions/{CATEGORY}/config.

    Required by backend (typical fields):
      - name: str
      - description: str
      - category: str
      - org_id: str
      - projectID: str           # NOTE: camelCase as required by backend
      - logo: str
      - ui_form: list

    Optional/variable:
      - config: dict
      - enabled: bool
    """
    name: str
    description: str
    category: str
    org_id: str
    projectID: str
    logo: str
    ui_form: list
    config: dict
    enabled: bool

class Connectors:
    def __init__(self, http: HttpClient):
        self.http = http
        self.google_drive = GoogleDrive(http)

    # POST /actions/{CATEGORY}/{ACTION}/{connector_id?}
    def action(self, category: str, action: str, connector_id: Optional[str] = None, *, body: Optional[dict] = None, projectID: Optional[str] = None) -> Any:
        path = f"/actions/{category}/{action}/{connector_id}" if connector_id else f"/actions/{category}/{action}"
        params = {"projectID": projectID} if projectID else None
        return self.http.request("POST", path, params=params, json=body)

    # POST /actions/{CATEGORY}/config?projectID=...
    def set_config(self, category: str, project_id: str, body: ConnectorConfigBody | dict) -> Any:
        # Ensure body contains the required camelCase field expected by the backend
        json_body = {**(body or {}), "projectID": project_id}
        return self.http.request("POST", f"/actions/{category}/config", params={"projectID": project_id}, json=json_body)

    # GET /actions/{CATEGORY}/config/{projectID}
    def get_config(self, category: str, project_id: str) -> Any:
        return self.http.request("GET", f"/actions/{category}/config/{project_id}")
