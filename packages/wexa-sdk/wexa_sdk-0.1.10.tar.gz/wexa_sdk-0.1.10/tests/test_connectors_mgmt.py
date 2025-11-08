from wexa_sdk import WexaClient


def test_connectors_mgmt_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # list variants
    c.connectors_mgmt.list()
    c.connectors_mgmt.list("p1")
    c.connectors_mgmt.list_by_project_id("p1")

    # get
    c.connectors_mgmt.get_by_id("cid1")
    c.connectors_mgmt.get_by_id_path("cid1")

    # delete variants
    c.connectors_mgmt.delete("cid1")
    c.connectors_mgmt.delete("cid1", project_id="p1")
    c.connectors_mgmt.delete_by_id_path("cid1", project_id="p1")

    # status + triggers
    c.connectors_mgmt.update_status(new_status="active", connectorID="cid1", data_loader_config={})
    c.connectors_mgmt.list_trigger_actions("p1")
    c.connectors_mgmt.list_trigger_actions_by_project("p1")

    i = 0
    assert calls[i] == ("GET", "/connectors/", None, None); i += 1
    assert calls[i] == ("GET", "/connectors/", {"projectID": "p1"}, None); i += 1
    assert calls[i] == ("GET", "/connectors/p1", None, None); i += 1
    assert calls[i] == ("GET", "/v1/connector/cid1", None, None); i += 1
    assert calls[i] == ("GET", "/connector/cid1", None, None); i += 1
    assert calls[i] == ("DELETE", "/v1/connector/cid1", None, None); i += 1
    assert calls[i] == ("DELETE", "/v1/connector/cid1", {"projectID": "p1"}, None); i += 1
    assert calls[i] == ("DELETE", "/connector/cid1", {"projectID": "p1"}, None); i += 1
    assert calls[i] == ("POST", "/connectors/change_status", None, {"new_status": "active", "connectorID": "cid1", "data_loader_config": {}}); i += 1
    assert calls[i] == ("GET", "/connectors/trigger_actions", {"projectID": "p1"}, None); i += 1
    assert calls[i] == ("GET", "/connectors/p1/trigger_actions", {"projectID": "p1"}, None); i += 1
