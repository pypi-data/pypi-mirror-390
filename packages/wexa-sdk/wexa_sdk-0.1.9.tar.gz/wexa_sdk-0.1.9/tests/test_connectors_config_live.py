import os
import json
import time
import pytest
from wexa_sdk import WexaClient

BASE_URL = os.getenv("WEXA_BASE_URL", "https://api.wexa.ai")
API_KEY = os.getenv("WEXA_API_KEY")
PROJECT_ID = "68c3b68b9120a0bdfb281d89"  # provided
CATEGORY = "content_creator"
ORG_ID = os.getenv("WEXA_ORG_ID") or os.getenv("NEXT_PUBLIC_ORG_ID")


@pytest.mark.integration
def test_content_creator_config_live_get_then_set():
    """
    Live test for connector config:
    1) GET /actions/{CATEGORY}/config/{projectID}
    2) POST /actions/{CATEGORY}/config?projectID=...

    Skips when WEXA_API_KEY or ORG_ID (WEXA_ORG_ID/NEXT_PUBLIC_ORG_ID) is not set.
    """
    if not API_KEY:
        pytest.skip("Set WEXA_API_KEY in the environment to run this live test")
    if not ORG_ID:
        pytest.skip("Set WEXA_ORG_ID or NEXT_PUBLIC_ORG_ID to run this live test")

    client = WexaClient(base_url=BASE_URL, api_key=API_KEY)

    # Step 1: GET current config
    current = client.connectors.get_config(CATEGORY, PROJECT_ID)
    print(json.dumps({"current": current}, indent=2))

    # Step 2: Build required payload from GET response and env
    cfg = (current or {}).get("config", {})
    # Ensure unique name to avoid 'Connector with the same name already exists'
    base_name = cfg.get("name") or "Content creator"
    unique_name = f"{base_name}-{int(time.time())}"
    update_body = {
        # required by backend
        "name": unique_name,
        "description": cfg.get("description") or "",
        "category": CATEGORY,
        "org_id": ORG_ID,
        "projectID": PROJECT_ID,
        "logo": cfg.get("logo") or "",
        "ui_form": cfg.get("ui_form") or [],
        # optional but present in GET; include to be safe
        "config": cfg.get("config") or {},
        # toggle
        "enabled": True,
    }

    updated = client.connectors.set_config(CATEGORY, PROJECT_ID, update_body)
    print(json.dumps({"updated": updated}, indent=2))

    # Basic assertions
    assert isinstance(updated, dict)
