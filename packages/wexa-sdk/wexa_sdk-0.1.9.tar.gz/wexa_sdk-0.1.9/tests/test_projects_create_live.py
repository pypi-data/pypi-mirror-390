import time
import json
import pytest
from wexa_sdk import WexaClient

# ===== Configure for live run =====
BASE_URL = "https://api.wexa.ai"
API_KEY = "506af7e9-9309-4fdf-b004-8d4cb09dfc05"
ORG_ID = "66f3cdde22bc63eb7490e23e"


@pytest.mark.integration
def test_projects_create_live_published():
    """
    Live test that creates a new project in the given org with status "published".
    This will mutate production data.

    To run:
        pytest -s tests/test_projects_create_live.py
    """
    if not API_KEY or "REPLACE_WITH" in API_KEY or not ORG_ID:
        pytest.skip("Edit BASE_URL, API_KEY, ORG_ID before running this live test")

    c = WexaClient(base_url=BASE_URL, api_key=API_KEY)

    name = f"SDK Create Test {int(time.time())}"
    body = {
        "orgId": ORG_ID,
        "projectName": name,
        "description": "Created via live integration test",
        "coworker_role": "Tester",
        "status": "published",
    }
    res = c.projects.create(body)

    print(json.dumps(res, indent=2))

    assert isinstance(res, dict)
    created = res.get("data", res)
    assert isinstance(created, dict)
    assert "_id" in created
