from typing import Optional, Dict, Any
from timeback.http import HttpClient
from timeback.logs import logger
from timeback.models.request import TimebackDeleteAgentRequest

log = logger.configure_logging(__name__, log_level="DEBUG")


def delete_agent(
    http: HttpClient, request: TimebackDeleteAgentRequest
) -> Optional[Dict[str, Any]]:
    """Delete an agent for a user.

    DELETE /ims/oneroster/rostering/v1p2/users/{userId}/agents/{agentSourcedId}

    Args:
        http: Injected HTTP client for making requests
        request: Request containing user_id and agent_sourced_id

    Returns:
        Optional[Dict[str, Any]]: Raw provider response (None for no-content)
    """
    log.debug(f"Request: {request}")
    log.debug(f"Deleting agent '{request.agent_sourced_id}' for user '{request.user_id}'")
    data = http.delete(
        f"/ims/oneroster/rostering/v1p2/users/{request.user_id}/agents/{request.agent_sourced_id}"
    )
    return data
