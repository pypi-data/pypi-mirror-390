import os
import json
import pytest
from wexa_sdk import WexaClient

BASE_URL = os.getenv("WEXA_BASE_URL", "https://api.wexa.ai")
API_KEY = os.getenv("WEXA_API_KEY")
PROJECT_ID = "68c3b68b9120a0bdfb281d89"  # provided


@pytest.mark.integration
def test_tables_create_live_wexa_sdk():
    """
    Live test to create a table with random columns (no triggers).
    Skips if WEXA_API_KEY is not set.
    """
    if not API_KEY:
        pytest.skip("Set WEXA_API_KEY in your environment to run this live test")

    client = WexaClient(base_url=BASE_URL, api_key=API_KEY)

    table_name = "wexa_sdk"
    spec = {
        "table_name": table_name,
        "columns": [
            {"column_name": "email", "column_type": "String", "column_id": "email"},
            {"column_name": "age", "column_type": "Number", "column_id": "age"},
            {"column_name": "tags", "column_type": "Array", "column_id": "tags", "array_type": "String", "default_value": []},
            {"column_name": "status", "column_type": "Enum", "column_id": "status", "enum_options": ["active", "inactive"], "default_value": "active"},
        ],
    }

    res = client.tables.create_table(PROJECT_ID, spec)
    print(json.dumps(res, indent=2))

    assert isinstance(res, dict)
