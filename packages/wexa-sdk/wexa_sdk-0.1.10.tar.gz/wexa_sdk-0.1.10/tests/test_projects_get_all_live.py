import pytest
import json
from wexa_sdk import WexaClient

# ===== Configure these before running =====
# Use prod or local API base URL
BASE_URL = "https://api.wexa.ai"  # or "http://localhost:5000"
API_KEY = "506af7e9-9309-4fdf-b004-8d4cb09dfc05"
TEST_USER_ID = "66f3cdde22bc63eb7490e23c"
TEST_ORG_ID = "66f3cdde22bc63eb7490e23e"


@pytest.mark.integration
def test_projects_get_all_live():
    """
    Live integration test for Projects.get_all() against a real API.

    Usage:
      1) Edit BASE_URL, API_KEY, TEST_USER_ID, TEST_ORG_ID at the top of this file.
      2) Run: pytest -q tests/test_projects_get_all_live.py
    """
    base_url = BASE_URL
    api_key = API_KEY
    user_id = TEST_USER_ID
    org_id = TEST_ORG_ID

    if (not api_key) or ("REPLACE_WITH_API_KEY" in api_key) or (not user_id) or (not org_id):
        pytest.skip("Edit BASE_URL, API_KEY, TEST_USER_ID, TEST_ORG_ID in this file to run this live test")

    c = WexaClient(base_url=base_url, api_key=api_key)
    res = c.projects.get_all(
        status="published",
        user_id=user_id,
        org_id=org_id,
        page=1,
        limit=12,
    )

    # Print the response for inspection
    print(json.dumps(res, indent=2))

    assert isinstance(res, dict)

    # Backend may return either a list wrapper or items/count; accept both
    if "projectList" in res:
        assert isinstance(res["projectList"], list)
        assert "totalCount" in res
    else:
        # fallback shape if API differs
        assert "items" in res
        assert isinstance(res["items"], list)
