from wexa_sdk import WexaClient


def test_create_table_rich_spec(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    spec = {
        "table_name": "Customers",
        "columns": [
            {"column_name": "email", "column_type": "String", "column_id": "email"},
            {
                "column_name": "tags",
                "column_type": "Array",
                "column_id": "tags",
                "array_type": "String",
                "default_value": [],
            },
            {
                "column_name": "status",
                "column_type": "Enum",
                "column_id": "status",
                "enum_options": ["active", "inactive"],
                "default_value": "active",
            },
            {
                "column_name": "profile",
                "column_type": "Object",
                "column_id": "profile",
                "object_fields": [{"key": "firstName", "keyType": "String"}],
            },
        ],
        "triggers": [
            {"goal": "audit new row", "event": "row_created", "trigger_type": "coworker"}
        ],
    }

    project_id = "proj123"
    c.tables.create_table(project_id, spec)

    # Assertions
    assert calls[0][0] == "POST"
    assert calls[0][1] == "/create/table"
    assert calls[0][2] == {"projectID": project_id}
    body = calls[0][3]
    assert body["projectID"] == project_id
    assert body["table_name"] == "Customers"
    assert isinstance(body.get("columns"), list)
