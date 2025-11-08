from wexa_sdk import WexaClient


def test_executions_start_posts_payload_and_query(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls["method"] = method
        calls["path"] = path
        calls["params"] = params
        calls["json"] = json
        return {"execution_id": "e1"}

    c.http.request = fake_request  # type: ignore

    res = c.executions.start({"agentflow_id": "a1", "inputs": {}}, projectID="p1")

    assert calls["method"] == "POST"
    assert calls["path"] == "/execute_flow"
    assert calls["params"] == {"projectID": "p1"}
    assert calls["json"] == {"agentflow_id": "a1", "inputs": {}}
    assert res == {"execution_id": "e1"}
