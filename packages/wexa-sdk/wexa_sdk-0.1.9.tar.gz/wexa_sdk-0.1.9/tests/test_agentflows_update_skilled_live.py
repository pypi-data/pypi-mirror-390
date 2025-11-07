import os
import json
import pytest
from wexa_sdk import WexaClient

BASE_URL = os.getenv("WEXA_BASE_URL", "https://api.wexa.ai")
API_KEY = os.getenv("WEXA_API_KEY") or ""
PROJECT_ID = os.getenv("PROJECT_ID", "68c3b68b9120a0bdfb281d89")
AGENTFLOW_ID = os.getenv("AGENTFLOW_ID", "6901def632348b1fae4c0e6a")
AGENT_ID = os.getenv("AGENT_ID", "6901def7e643a25d472d0952")

# The user-provided payload (trimmed to minimal required where possible)
PAYLOAD = {
    "role": "Create Call",
    "title": "Create a Call",
    "skills": ["6901dbf973f8d927fe126fad"],
    "prompt": {
        "display_template": "...",  # large rich text omitted for brevity
        "variables": [],
        "template": "..."
    },
    "context": [],
    "triggers": [],
    "llm": {"model": "bedrock/eu.anthropic.claude-3-7-sonnet-20250219-v1:0", "max_tokens": 10000, "temperature": 0},
    "role_description": "Creating a calling agent",
    "memory": {"memory_type": "lt"},
    "has_knowledge_base": False,
    "is_user_specific_task": False,
    "is_preview_mode_enabled": False,
}


@pytest.mark.integration
def test_update_skilled_agent_live():
    if not API_KEY:
        pytest.skip("Set WEXA_API_KEY to run this live test")

    client = WexaClient(base_url=BASE_URL, api_key=API_KEY)
    resp = client.agentflows.update_skilled_agent(
        agentflow_id=AGENTFLOW_ID,
        agent_id=AGENT_ID,
        projectID=PROJECT_ID,
        body=PAYLOAD,
    )
    print(json.dumps(resp, indent=2))
    assert isinstance(resp, dict) or isinstance(resp, list)
