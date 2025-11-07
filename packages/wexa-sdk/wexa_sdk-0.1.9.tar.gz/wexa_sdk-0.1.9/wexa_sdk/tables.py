from __future__ import annotations
from typing import Any, Optional, TypedDict, List, Dict, Union

from .core.http import HttpClient

class ObjectField(TypedDict, total=False):
    """Field descriptor for object-type columns."""
    key: str
    keyType: str


class AgentflowTrigger(TypedDict, total=False):
    """Trigger configuration attached to a table or column.

    Note: exact schemas for `condition` and `filters` may evolve; we leave them open.
    """
    _id: str
    id: str
    condition: Dict[str, Any]
    name: Optional[str]
    goal: str
    agentflow_id: Optional[str]
    filters: List[Dict[str, Any]]
    schedule_time: Optional[str]
    event: str
    start_from_agent_id: Optional[str]
    trigger_type: str  # e.g. "coworker"


class Column(TypedDict, total=False):
    """Column definition for a table."""
    column_name: str
    column_type: str
    column_id: str
    array_type: Optional[str]
    default_value: Union[Any, List[Any], Dict[str, Any]]
    object_fields: List[ObjectField]
    triggers: List[AgentflowTrigger]
    enum_options: List[str]


class CreateTableInput(TypedDict, total=False):
    """Typed input for creating a table.

    Required keys: projectID, table_name
    Optional keys: columns, triggers
    """
    projectID: str
    table_name: str
    columns: List[Column]
    triggers: List[AgentflowTrigger]


class Tables:
    def __init__(self, http: HttpClient):
        self.http = http

    # Tables
    def create_table(self, project_id: str, spec: CreateTableInput):
        """Create a new table.

        Args:
            project_id: The project ID (placed into query as `projectID`).
            spec: Table specification containing at least `table_name`.

        The backend expects `projectID` in both query params and JSON body.
        """
        # API expects projectID as query param and in body with 'projectID' casing
        params = {"projectID": project_id}
        body = {"projectID": project_id, **spec}
        return self.http.request("POST", "/create/table", params=params, json=body)

    def list_tables(self, project_id: str):
        return self.http.request("GET", f"/storage/{project_id}")

    def get_table(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}")

    def get_table_view(self, table_id: str):
        return self.http.request("GET", f"/table/view/{table_id}")

    def rename_table(self, project_id: str, table_id: str, new_name: str):
        return self.http.request("POST", f"/table/rename/{project_id}", json={"tableId": table_id, "newName": new_name})

    # Columns
    def get_columns(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/column/storage/{project_id}/{table_id}")

    def edit_columns(self, table_id: str, spec: dict):
        return self.http.request("POST", f"/edit/columns/{table_id}", json=spec)

    def delete_column(self, project_id: str, column_id: str):
        return self.http.request("DELETE", f"/delete/column/{project_id}", json={"columnId": column_id})

    # Records
    def create_record(self, project_id: str, table_id: str, record: dict):
        return self.http.request("POST", f"/storage/{project_id}/{table_id}", json=record)

    def get_record(self, project_id: str, table_id: str, record_id: str):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}/{record_id}")

    def update_record(self, project_id: str, table_id: str, record_id: str, record: dict):
        return self.http.request("PUT", f"/storage/{project_id}/{table_id}/{record_id}", json=record)

    def delete_record(self, project_id: str, table_id: str, record_id: str):
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}/{record_id}")

    def list_records(self, project_id: str, table_id: str, query: Optional[dict] = None):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}", params=query)

    def bulk_upsert(self, project_id: str, table_id: str, records: list[dict]):
        return self.http.request("POST", f"/bulk/storage/{project_id}/{table_id}", json={"records": records})

    def export(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/table_data/storage/{table_id}/export")
