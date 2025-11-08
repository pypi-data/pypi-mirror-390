from wexa_sdk import WexaClient


def test_tables_endpoints(monkeypatch):
    c = WexaClient(base_url="https://api.wexa.ai", api_key="key")
    calls = []

    def fake_request(method, path, *, params=None, json=None, headers=None):  # type: ignore
        calls.append((method, path, params, json))
        return {"ok": True}

    c.http.request = fake_request  # type: ignore

    # Tables
    c.tables.create_table("proj", {"table_name": "T"})
    c.tables.list_tables("proj")
    c.tables.get_table("proj", "tbl")
    c.tables.get_table_view("tbl")
    c.tables.rename_table("proj", "tbl", "New")

    # Columns
    c.tables.get_columns("proj", "tbl")
    c.tables.edit_columns("tbl", {"add": []})
    c.tables.delete_column("proj", "col")

    # Records
    c.tables.create_record("proj", "tbl", {"a": 1})
    c.tables.get_record("proj", "tbl", "rec")
    c.tables.update_record("proj", "tbl", "rec", {"a": 2})
    c.tables.delete_record("proj", "tbl", "rec")
    c.tables.list_records("proj", "tbl", {"limit": 2})
    c.tables.bulk_upsert("proj", "tbl", [{"a": 1}])
    c.tables.export("proj", "tbl")

    assert calls[0] == ("POST", "/create/table", {"projectID": "proj"}, {"projectID": "proj", "table_name": "T"})
    assert calls[1] == ("GET", "/storage/proj", None, None)
    assert calls[2] == ("GET", "/storage/proj/tbl", None, None)
    assert calls[3] == ("GET", "/table/view/tbl", None, None)
    assert calls[4] == ("POST", "/table/rename/proj", None, {"tableId": "tbl", "newName": "New"})
    assert calls[5] == ("GET", "/column/storage/proj/tbl", None, None)
    assert calls[6] == ("POST", "/edit/columns/tbl", None, {"add": []})
    assert calls[7] == ("DELETE", "/delete/column/proj", None, {"columnId": "col"})
    assert calls[8] == ("POST", "/storage/proj/tbl", None, {"a": 1})
    assert calls[9] == ("GET", "/storage/proj/tbl/rec", None, None)
    assert calls[10] == ("PUT", "/storage/proj/tbl/rec", None, {"a": 2})
    assert calls[11] == ("DELETE", "/storage/proj/tbl/rec", None, None)
    assert calls[12] == ("GET", "/storage/proj/tbl", {"limit": 2}, None)
    assert calls[13] == ("POST", "/bulk/storage/proj/tbl", None, {"records": [{"a": 1}]})
    assert calls[14] == ("GET", "/table_data/storage/tbl/export", None, None)
