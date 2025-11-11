"""Add Agent endpoint for OneRoster Rostering.

POST /ims/oneroster/rostering/v1p2/users/{userId}/agents

Builds the full path with user_id from request, performs the HTTP POST via the injected
`HttpClient`, and returns the raw response dictionary.
"""

from typing import Any, Dict

from timeback.http import HttpClient
from timeback.models.request import TimebackAddAgentRequest
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def add_agent(http: HttpClient, request: TimebackAddAgentRequest) -> Dict[str, Any]:
    """Add an agent for a user.

    Args:
        http: Injected HTTP client for making requests
        request: Request containing user_id and agent_sourced_id

    Returns:
        Dict containing the provider's response (may include message and other fields)
    """
    log.debug(f"Request: {request}")
    body: Dict[str, Any] = {"agentSourcedId": request.agent_sourced_id}
    log.debug(f"POST body: {body}")
    data: Dict[str, Any] = http.post(
        f"/ims/oneroster/rostering/v1p2/users/{request.user_id}/agents", json=body
    )
    log.debug(f"Raw Data: {data}")
    return data

