from __future__ import annotations
from typing import Optional, TypedDict
from .core.http import HttpClient


class AgentflowCreateBody(TypedDict, total=False):
    """Body for creating an AgentFlow (Coworker).

    Required:
      - name: str
      - description: str
      - role: str
      - projectID: str

    Optional: backend-supported fields like agents/processflow, anomaly_detection, cron_details, etc.
    """
    name: str
    description: str
    role: str
    projectID: str

class AgentFlows:
    def __init__(self, http: HttpClient):
        self.http = http

    def list(
        self,
        project_id: str | None = None,
        projectID: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ):
        # API expects 'projectID' (capital D); accept both and normalize
        pid = projectID or project_id
        params: dict | None = None
        if pid is not None or skip is not None or limit is not None:
            params = {}
            if pid is not None:
                params["projectID"] = pid
            if skip is not None:
                params["skip"] = skip
            if limit is not None:
                params["limit"] = limit
        return self.http.request("GET", "/agentflows", params=params)

    def get(self, id: str):
        return self.http.request("GET", f"/agentflow/{id}")

    def create(self, body: AgentflowCreateBody, projectID: Optional[str] = None):
        """
        Create a new AgentFlow (Coworker).

        Query params:
          - projectID (str, required): Project to create the AgentFlow in. If not provided
            as an argument, this will be inferred from body['projectID'] or body['projectId'].

        Headers:
          - x-api-key (str, required)

        Body (application/json):
          - name (str, required)
          - description (str, required)
          - role (str, required)
          - projectID (str, required)
          - ...additional optional fields supported by backend (e.g., agents, anomaly_detection, cron_details)

        Returns:
          - dict: The created AgentFlow JSON (e.g., keys: _id, name, role, projectID, ...)
        """
        # include projectID in query if provided, or infer from body
        pid = projectID or body.get("projectID") or body.get("projectId")
        params = {"projectID": pid} if pid else None
        return self.http.request("POST", "/agentflow/", params=params, json=body)

    def update(self, id: str, body: dict):
        return self.http.request("PUT", f"/agentflow/{id}", json=body)

    # Typed body for updating a skilled agent to enable IDE suggestions
    class UpdateSkilledAgentBody(TypedDict, total=False):
        """Body for updating a skilled agent within an AgentFlow.

        Required (per API docs):
          - role: str
          - title: str
          - skills: list[str]
          - prompt: { template: str, variables: list, display_template: str }
          - context: list
          - triggers: list
          - llm: { model: str, max_tokens: int, temperature: int }
          - role_description: str
          - memory: { memory_type: str }
          - has_knowledge_base: bool
          - is_user_specific_task: bool
          - is_preview_mode_enabled: bool
        """
        role: str
        title: str
        skills: list[str]
        prompt: dict
        context: list
        triggers: list
        llm: dict
        role_description: str
        memory: dict
        has_knowledge_base: bool
        is_user_specific_task: bool
        is_preview_mode_enabled: bool

    def update_skilled_agent(self, agentflow_id: str, agent_id: str, *, projectID: str, body: UpdateSkilledAgentBody | dict):
        """Update a skilled agent within an AgentFlow.

        Endpoint: POST /agentflow/{agentflow_id}/update/skilled/{agent_id}?projectID=...

        Args:
            agentflow_id: ID of the AgentFlow
            agent_id: ID of the skilled agent inside the AgentFlow
            projectID: Project ID (query param, required)
            body: Update payload, see UpdateSkilledAgentBody for suggested keys
        """
        params = {"projectID": projectID} if projectID else None
        path = f"/agentflow/{agentflow_id}/update/skilled/{agent_id}"
        return self.http.request("POST", path, params=params, json=body)
