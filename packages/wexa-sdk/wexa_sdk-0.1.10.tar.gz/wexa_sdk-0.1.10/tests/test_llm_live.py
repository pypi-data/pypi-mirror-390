import os
import json
import pytest
from wexa_sdk import WexaClient


BASE_URL = "https://testing.api.wexa.ai"
API_KEY = "265d37d8-3496-4758-b0d5-dc64cc29b444"


@pytest.mark.integration
def test_llm_call_live():
    if not os.getenv("WEXA_LLM_LIVE"):
        pytest.skip("Set WEXA_LLM_LIVE=1 to run this live test")

    c = WexaClient(base_url=BASE_URL, api_key=API_KEY)
    body = {
        "model": "bedrock/amazon.nova-pro-v1",
        "messages": [{"role": "user", "content": "Hello, how are you?"}],
    }
    res = c.llm.llm_call(body)  # type: ignore[arg-type]
    print(json.dumps(res, indent=2))
    assert res is not None


