from wexa_sdk import WexaClient


def test_agentflows_crud(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # create with projectID in body -> should go to query as well
    c.agentflows.create({"name": "N", "projectID": "p1"})
    # update
    c.agentflows.update("af1", {"name": "U"})
    # delete
    c.agentflows.delete("p1", "af1")

    assert calls[0][0] == "POST" and calls[0][1] == "/agentflow/" and calls[0][2] == {"projectID": "p1"}
    assert calls[1][0] == "PUT" and calls[1][1] == "/agentflow/af1"
    assert calls[2][0] == "DELETE" and calls[2][1] == "/agentflow/p1/af1"
