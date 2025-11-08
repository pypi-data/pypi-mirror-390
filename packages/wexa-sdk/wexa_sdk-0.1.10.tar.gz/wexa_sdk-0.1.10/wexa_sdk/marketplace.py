from __future__ import annotations
from typing import Any, Dict

from .core.http import HttpClient

class Marketplace:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /public/connectors/all?search_key=...&projectID=...&filter_type=...
    def list_connectors(self, *, search_key: str, projectID: str, filter_type: str):
        params: Dict[str, Any] = {"search_key": search_key, "projectID": projectID, "filter_type": filter_type}
        return self.http.request("GET", "/public/connectors/all", params=params)

    # GET /public/marketplace/coworkers?search_key=...&limit=...
    def list_coworkers(self, *, search_key: str, limit: int | str):
        params: Dict[str, Any] = {"search_key": search_key, "limit": limit}
        return self.http.request("GET", "/public/marketplace/coworkers", params=params)

    # GET /public/marketplace/coworker/{coworker_id}
    def get_coworker_by_id(self, coworker_id: str):
        return self.http.request("GET", f"/public/marketplace/coworker/{coworker_id}")

    # POST /marketplace/coworker/{coworker_id}/purchase?organization_id=...
    def purchase_coworker(self, coworker_id: str, *, organization_id: str, body: Dict[str, Any] | None = None):
        params = {"organization_id": organization_id}
        return self.http.request("POST", f"/marketplace/coworker/{coworker_id}/purchase", params=params, json=(body or {}))

    # GET /marketplace/coworker/update/{coworker_id}/check
    def check_coworker_update(self, coworker_id: str):
        return self.http.request("GET", f"/marketplace/coworker/update/{coworker_id}/check")
