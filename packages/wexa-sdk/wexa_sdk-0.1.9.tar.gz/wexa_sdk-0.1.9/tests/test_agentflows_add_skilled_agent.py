from wexa_sdk import WexaClient


def test_agentflows_add_skilled_agent_requests(monkeypatch):
    client = WexaClient(base_url="https://api.wexa.ai", api_key="key")

    captured = {}

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        return {"ok": True}

    client.http.request = fake_request  # type: ignore

    body = {
        "_id": "agent-1",
        "role": "assistant",
        "title": "Writer",
        "skills": ["content_writer"],
        "context": [],
        "llm": {"model": "gpt-4o", "max_tokens": 512, "temperature": 0.7},
        "memory": {"memory_type": "short_term"},
        "agent_type": "skilled",
        "role_description": "Creates content",
        "prompt": {"template": "...", "variables": [], "display_template": "..."},
        "triggers": [],
        "has_knowledge_base": False,
        "is_user_specific_task": False,
        "is_preview_mode_enabled": False,
        "conditions": [],
    }

    resp = client.agentflows.add_skilled_agent(
        "aflow-123",
        projectID="proj-1",
        body=body,
    )

    assert captured["method"] == "POST"
    assert captured["path"] == "/agentflow/aflow-123/skilled"
    assert captured["params"] == {"projectID": "proj-1"}
    assert captured["json"] == body
    assert resp == {"ok": True}
