import os
import pytest
from wexa_sdk import WexaClient

pytestmark = pytest.mark.integration

missing_env = not os.getenv("WEXA_BASE_URL") or not os.getenv("WEXA_API_KEY")

@pytest.mark.skipif(missing_env, reason="WEXA_BASE_URL/WEXA_API_KEY not set")
def test_marketplace_lists_coworkers():
    c = WexaClient(base_url=os.environ["WEXA_BASE_URL"], api_key=os.environ["WEXA_API_KEY"])
    res = c.marketplace.list_coworkers(search_key="", limit=1)
    assert isinstance(res, dict)
