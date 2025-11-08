import os
import json
import pytest
from wexa_sdk import WexaClient


# Live test uses provided base URL and API key
BASE_URL = "https://testing.api.wexa.ai"
API_KEY = "265d37d8-3496-4758-b0d5-dc64cc29b444"


@pytest.mark.integration
def test_projects_mcp_connector_testing_live():
    project_name = os.getenv("WEXA_TEST_PROJECT_NAME")
    if not project_name:
        pytest.skip("Set WEXA_TEST_PROJECT_NAME to run this live test")

    c = WexaClient(base_url=BASE_URL, api_key=API_KEY)
    res = c.projects.get_by_project_name(project_name)

    # Print for visibility when running live
    print(json.dumps(res, indent=2))

    assert res is not None


