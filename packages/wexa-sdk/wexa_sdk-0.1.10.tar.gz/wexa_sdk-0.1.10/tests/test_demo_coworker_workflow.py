import os
import time
import json
import pytest

from wexa_sdk import WexaClient

BASE = os.environ.get("WEXA_BASE_URL", "https://api.wexa.ai")
API_KEY = os.environ.get("WEXA_API_KEY")
PROJECT_ID = os.environ.get("WEXA_PROJECT_ID", "69088bf4121a635f1301ad8c")


@pytest.mark.skipif(not API_KEY, reason="Set WEXA_API_KEY to run this integration test")
def test_coworker_create_or_load_and_execute():
    c = WexaClient(base_url=BASE, api_key=API_KEY)
    # Use a mostly-unique name per run to avoid conflicts
    name = f"InvoiceProcessor-{int(time.time()) % 100000}"

    def get_by_name(name: str, project_id: str):
        skip, limit = 0, 100
        while True:
            # Some environments reject skip=0; omit skip on first page
            if skip > 0:
                page = c.agentflows.list(projectID=project_id, skip=skip, limit=limit) or {}
            else:
                page = c.agentflows.list(projectID=project_id, limit=limit) or {}
            arr = page.get("agentflows") or page.get("data") or []
            for af in arr:
                if af.get("name") == name:
                    return af
            if len(arr) < limit:
                return None
            skip += limit

    af = get_by_name(name, PROJECT_ID)
    if not af:
        body = {
            "name": name,
            "description": "created via SDK test",
            "role": "SDK_ROLE",
            "projectID": PROJECT_ID,
        }
        af = c.agentflows.create(body, projectID=PROJECT_ID)
        assert af and af.get("_id"), "Agentflow creation failed"

    # Execute the flow
    payload = {
        "agentflow_id": af["_id"],
        "executed_by": "sdk@test",
        "goal": "Demo run",
        "input_variables": {"echo": "hello"},
        "projectID": PROJECT_ID,
    }
    started = c.executions.start(payload, projectID=PROJECT_ID)
    assert started and started.get("_id"), "Execution start failed"

    # Try a brief wait; if it times out, fetch current state and finish
    try:
        res = c.executions.wait(started["_id"], timeout_ms=15_000)
    except Exception:
        res = c.executions.get(started["_id"])

    assert isinstance(res, dict)
    # Print (visible in CI logs) for manual inspection if needed
    print(json.dumps({
        "agentflow": {"_id": af.get("_id"), "name": af.get("name")},
        "execution": {"_id": started.get("_id"), "status": res.get("status")}
    })[:1000])
