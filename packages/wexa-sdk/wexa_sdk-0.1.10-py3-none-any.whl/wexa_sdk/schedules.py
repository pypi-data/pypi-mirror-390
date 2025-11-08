from __future__ import annotations
from typing import TypedDict, Optional, Dict, Any

from .core.http import HttpClient


class CoworkerScheduleCreateBody(TypedDict):
    coworker_id: str
    goal: Dict[str, Any]
    template: str
    display_template: str
    schedule: int


class CoworkerScheduleUpdateBody(TypedDict, total=False):
    goal: Dict[str, Any]
    template: str
    display_template: str
    schedule: int


class Schedules:
    def __init__(self, http: HttpClient):
        self.http = http

    def list_coworker_schedules(
        self,
        coworker_id: str | None,
        *,
        projectID: str,
        limit: int = 20,
        page_no: int = 1,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search_key: Optional[str] = None,
    ):
        """
        GET /schedules/coworker

        Query params: projectID (required), limit, page_no, coworker_id, status, type, search_key
        """
        params: Dict[str, Any] = {"projectID": projectID, "limit": limit, "page_no": page_no}
        if coworker_id:
            params["coworker_id"] = coworker_id
        if status is not None:
            params["status"] = status
        if type is not None:
            params["type"] = type
        if search_key is not None:
            params["search_key"] = search_key
        return self.http.request("GET", "/schedules/coworker", params=params)

    def create_coworker_schedule(self, *, projectID: str, body: CoworkerScheduleCreateBody):
        """
        POST /schedule/coworker?projectID=...
        Body: coworker_id, goal, template, display_template, schedule
        """
        params = {"projectID": projectID}
        return self.http.request("POST", "/schedule/coworker", params=params, json=body)

    def get_coworker_schedule(self, id: str):
        """
        GET /schedule/coworker/{id}
        """
        return self.http.request("GET", f"/schedule/coworker/{id}")

    def update_coworker_schedule(self, id: str, *, projectID: str, body: CoworkerScheduleUpdateBody):
        """
        PATCH /schedule/coworker/{id}?projectID=...
        """
        params = {"projectID": projectID}
        return self.http.request("PATCH", f"/schedule/coworker/{id}", params=params, json=body)

    def delete_coworker_schedule(self, id: str, *, projectID: str):
        """
        DELETE /schedule/coworker/{id}?projectID=...
        """
        params = {"projectID": projectID}
        return self.http.request("DELETE", f"/schedule/coworker/{id}", params=params)


