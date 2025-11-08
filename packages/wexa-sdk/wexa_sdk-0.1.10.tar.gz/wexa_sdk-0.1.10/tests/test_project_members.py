from wexa_sdk import WexaClient


def test_project_members_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.project_members.summary("p1")
    c.project_members.list("p1")

    assert calls[0] == ("GET", "/project-member/p1/summary", None, None)
    assert calls[1] == ("GET", "/project-member/p1", None, None)
