from wexa_sdk import WexaClient


def test_inbox_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.inbox.create({"x": 1})
    c.inbox.list("p1", limit=2)
    c.inbox.update_runtime("p1", {"a": 1})
    c.inbox.update_anomaly("p1", {"b": 2})
    c.inbox.update_preview("p1", {"c": 3})
    c.inbox.update_preview_by_execution("exec1", {"d": 4}, "p1")
    c.inbox.get("inb1", "p1")

    assert calls[0] == ("POST", "/inbox/create", None, {"x": 1})
    assert calls[1] == ("GET", "/inbox", {"projectID": "p1", "limit": 2}, None)
    assert calls[2] == ("POST", "/inbox/update/runtime_input/", {"projectID": "p1"}, {"a": 1})
    assert calls[3] == ("POST", "/inbox/update/anomaly_detection/", {"projectID": "p1"}, {"b": 2})
    assert calls[4] == ("POST", "/inbox/update/preview/", {"projectID": "p1"}, {"c": 3})
    assert calls[5] == ("POST", "/inbox/update/preview/exec1", {"projectID": "p1"}, {"d": 4})
    assert calls[6] == ("GET", "/inbox/inb1", {"projectID": "p1"}, None)
