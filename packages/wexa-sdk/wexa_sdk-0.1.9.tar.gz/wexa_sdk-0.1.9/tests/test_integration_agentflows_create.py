import os, time, json, pytest
from wexa_sdk import WexaClient
from wexa_sdk.core.http import ApiError

missing_env = not (os.getenv("WEXA_BASE_URL") and os.getenv("WEXA_API_KEY") and os.getenv("PROJECT_ID"))

@pytest.mark.integration
@pytest.mark.skipif(missing_env, reason="WEXA_BASE_URL/WEXA_API_KEY/PROJECT_ID not set")
def test_agentflows_create_get_delete():
    base = os.environ["WEXA_BASE_URL"]
    key = os.environ["WEXA_API_KEY"]
    pid = os.environ["PROJECT_ID"]

    c = WexaClient(base_url=base, api_key=key)

    body = {
        "name": f"sdk-integ-py-{int(time.time())}",
        "description": "integration-create via sdk",
        "role": "SDK_ROLE",
        "projectID": pid,
    }

    afid = None
    try:
        created = c.agentflows.create(body, projectID=pid)
        assert isinstance(created, dict)
        afid = created.get("_id") or created.get("id")
        assert afid and isinstance(afid, str)

        got = c.agentflows.get(afid)
        assert got.get("_id") == afid
        assert got.get("name") == body["name"]
    except ApiError as e:
        pytest.fail(f"API error: {e.status} {e.detail}")
    finally:
        if afid:
            try:
                c.agentflows.delete(pid, afid)
            except ApiError:
                pass
