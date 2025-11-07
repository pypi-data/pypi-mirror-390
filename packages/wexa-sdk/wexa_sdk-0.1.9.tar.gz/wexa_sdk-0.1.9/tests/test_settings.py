from wexa_sdk import WexaClient


def test_settings_get(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls["method"] = method
        calls["path"] = path
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    res = c.settings.get("p1")

    assert calls["method"] == "GET"
    assert calls["path"] == "/settings/p1"
    assert res == {"ok": True}
