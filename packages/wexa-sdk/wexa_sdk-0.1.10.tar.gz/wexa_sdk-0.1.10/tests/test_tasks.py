from wexa_sdk import WexaClient


def test_tasks_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.tasks.list("p1", limit=2, skip=1, created_by="u1")
    c.tasks.get("t1", "p1")
    c.tasks.pause("t1")
    c.tasks.resume("t1")
    c.tasks.stop("t1")

    assert calls[0] == ("GET", "/tasks/", {"projectID": "p1", "limit": 2, "skip": 1, "created_by": "u1"}, None)
    assert calls[1] == ("GET", "/task/t1", {"projectID": "p1"}, None)
    assert calls[2] == ("POST", "/task/t1/pause", None, None)
    assert calls[3] == ("POST", "/task/t1/resume", None, None)
    assert calls[4] == ("POST", "/task/t1/stop", None, None)
