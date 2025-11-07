from wexa_sdk import WexaClient


def test_marketplace_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    c.marketplace.list_connectors(search_key="", projectID="p1", filter_type="ALL")
    c.marketplace.list_coworkers(search_key="", limit=2)
    c.marketplace.get_coworker_by_id("cw1")
    c.marketplace.purchase_coworker("cw1", organization_id="org1", body={"plan": "pro"})
    c.marketplace.check_coworker_update("cw1")

    assert calls[0] == ("GET", "/public/connectors/all", {"search_key": "", "projectID": "p1", "filter_type": "ALL"}, None)
    assert calls[1] == ("GET", "/public/marketplace/coworkers", {"search_key": "", "limit": 2}, None)
    assert calls[2] == ("GET", "/public/marketplace/coworker/cw1", None, None)
    assert calls[3] == ("POST", "/marketplace/coworker/cw1/purchase", {"organization_id": "org1"}, {"plan": "pro"})
    assert calls[4] == ("GET", "/marketplace/coworker/update/cw1/check", None, None)
