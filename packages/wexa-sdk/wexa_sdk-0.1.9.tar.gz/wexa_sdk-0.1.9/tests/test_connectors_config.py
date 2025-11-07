from wexa_sdk import WexaClient


def test_connectors_config_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # set config -> POST /actions/{CATEGORY}/config?projectID=...
    c.connectors.set_config("content_creator", "p1", {"enabled": True})
    # get config -> GET /actions/{CATEGORY}/config/{projectID}
    c.connectors.get_config("content_creator", "p1")

    assert calls[0] == (
        "POST",
        "/actions/content_creator/config",
        {"projectID": "p1"},
        {"enabled": True},
    )
    assert calls[1] == (
        "GET",
        "/actions/content_creator/config/p1",
        None,
        None,
    )
