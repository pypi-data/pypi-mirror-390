"""Decision API client for Aegis Data Plane integration."""

from typing import Any

from .config import AegisConfig
from .http import AegisHttpClient
from .types import DecisionRequest, DecisionResponse, ToolCall


class DecisionClient:
    """Client for interacting with Aegis Decision API."""

    def __init__(self, config: AegisConfig):
        """Initialize decision client with configuration."""
        self.config = config
        self.http_client = AegisHttpClient(config)

    def decide(
        self,
        agent_id: str,
        tool_name: str,
        params: dict[str, Any],
        session: dict[str, Any] | None = None,
    ) -> DecisionResponse:
        """Request a decision for a tool call.

        Args:
            agent_id: Identifier for the agent making the request
            tool_name: Name of the tool being called
            params: Parameters for the tool call
            session: Optional session context

        Returns:
            DecisionResponse with allow/deny/sanitize/approval_needed result

        Raises:
            AegisError: For API errors or transport issues
        """
        request = DecisionRequest(
            agent_id=agent_id,
            tool=ToolCall(
                name=tool_name,
                params=params,
            ),
            session=session,
        )

        response_data = self.http_client.post_json(
            path="/v1/decision",
            json_data=request.model_dump(),
        )

        return DecisionResponse(**response_data)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.http_client.close()
