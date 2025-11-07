from __future__ import annotations
from typing import Any, Optional

from .core.http import HttpClient

class ConnectorsMgmt:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /connectors/?projectID=...
    def list(self, project_id: Optional[str] = None) -> Any:
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", "/connectors/", params=params)

    # GET /connectors/{projectID}
    def list_by_project_id(self, project_id: str) -> Any:
        return self.http.request("GET", f"/connectors/{project_id}")

    # GET /v1/connector/{id}
    def get_by_id(self, connector_id: str) -> Any:
        return self.http.request("GET", f"/v1/connector/{connector_id}")

    # GET /connector/{connector_id}
    def get_by_id_path(self, connector_id: str) -> Any:
        return self.http.request("GET", f"/connector/{connector_id}")

    # DELETE /v1/connector/{id}?projectID=...
    def delete(self, connector_id: str, *, project_id: Optional[str] = None) -> Any:
        params = {"projectID": project_id} if project_id else None
        return self.http.request("DELETE", f"/v1/connector/{connector_id}", params=params)

    # DELETE /connector/{connector_id}?projectID=...
    def delete_by_id_path(self, connector_id: str, *, project_id: str) -> Any:
        return self.http.request("DELETE", f"/connector/{connector_id}", params={"projectID": project_id})

    # POST /connectors/change_status
    def update_status(self, *, new_status: str, connectorID: str, data_loader_config: dict) -> Any:
        body = {"new_status": new_status, "connectorID": connectorID, "data_loader_config": data_loader_config}
        return self.http.request("POST", "/connectors/change_status", json=body)

    # GET /connectors/trigger_actions?projectID=...
    def list_trigger_actions(self, project_id: str) -> Any:
        return self.http.request("GET", "/connectors/trigger_actions", params={"projectID": project_id})

    # GET /connectors/{projectID}/trigger_actions
    def list_trigger_actions_by_project(self, project_id: str) -> Any:
        return self.http.request("GET", f"/connectors/{project_id}/trigger_actions", params={"projectID": project_id})
