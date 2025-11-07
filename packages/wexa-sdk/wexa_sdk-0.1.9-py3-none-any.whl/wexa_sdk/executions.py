from __future__ import annotations
import time
from typing import Any, Callable, Optional

from .core.http import HttpClient

DEFAULT_TERMINAL = {"completed", "failed", "canceled"}

class Executions:
    def __init__(self, http: HttpClient, polling: Optional[dict] = None):
        self.http = http
        self.polling = polling or {}

    def start(self, payload: dict, *, projectID: Optional[str] = None):
        params = {"projectID": projectID} if projectID else None
        return self.http.request("POST", "/execute_flow", json=payload, params=params)

    def get(self, execution_id: str):
        return self.http.request("GET", f"/execute_flow/{execution_id}")

    def monitor(self, agentflow_id: str):
        return self.http.request("GET", f"/execute_flow/{agentflow_id}/monitor")

    def pause(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/pause")

    def resume(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/resume")

    def cancel(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/cancel")

    def approve_preview(self, execution_id: str):
        return self.http.request("PUT", f"/execute_flow/{execution_id}/approve_preview")

    def approve_anomaly(self, execution_id: str):
        return self.http.request("PUT", f"/execute_flow/{execution_id}/approve_anomaly")

    def update_runtime_input(self, execution_id: str, body: dict):
        return self.http.request("PUT", f"/execute_flow/{execution_id}/runtime_input", json=body)

    def wait(self, execution_id: str, *, interval_ms: Optional[int] = None, timeout_ms: Optional[int] = None, is_terminal: Optional[Callable[[str], bool]] = None):
        interval = interval_ms or self.polling.get("intervalMs", 2000)
        timeout = timeout_ms or self.polling.get("timeoutMs", 30 * 60 * 1000)
        jitter = self.polling.get("jitter", 0.2)
        term = is_terminal or (lambda s: (s or "").lower() in DEFAULT_TERMINAL)

        start = time.time()
        while True:
            info = self.get(execution_id)
            status = (info.get("status") or info.get("state") or "").lower()
            if term(status):
                return info
            if (time.time() - start) * 1000 > timeout:
                raise TimeoutError("Execution wait timeout")
            j = 1 + ((2 * (time.time() % 1) - 1) * jitter)
            time.sleep(max(0.2, (interval * j) / 1000))
