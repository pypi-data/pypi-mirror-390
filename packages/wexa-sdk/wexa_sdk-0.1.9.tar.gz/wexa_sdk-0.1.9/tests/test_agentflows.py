import pytest
from wexa_sdk import WexaClient


def test_agentflows_list_builds_params(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls["method"] = method
        calls["path"] = path
        calls["params"] = params
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    res = c.agentflows.list(projectID="p1", skip=1, limit=2)

    assert calls["method"] == "GET"
    assert calls["path"] == "/agentflows"
    assert calls["params"] == {"projectID": "p1", "skip": 1, "limit": 2}
    assert res == {"ok": True}
