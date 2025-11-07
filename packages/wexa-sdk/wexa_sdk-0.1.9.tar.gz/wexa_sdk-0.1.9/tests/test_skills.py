from wexa_sdk import WexaClient


def test_skills_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.skills.create({"name": "s1"})
    c.skills.list("p1", limit=2)
    c.skills.list_by_category("p1", "LLM", limit=1)
    c.skills.get_by_id("sid1")
    c.skills.get_by_name("s1", "p1")

    assert calls[0] == ("POST", "/skills/", None, {"name": "s1"})
    assert calls[1] == ("GET", "/skills/", {"projectID": "p1", "limit": 2}, None)
    assert calls[2] == ("GET", "/skills/category", {"projectId": "p1", "category": "LLM", "limit": 1}, None)
    assert calls[3] == ("GET", "/skills/sid1", None, None)
    assert calls[4] == ("GET", "/skills/", {"name": "s1", "projectID": "p1"}, None)
