"""Get Agent For endpoint for OneRoster Rostering.

GET /ims/oneroster/rostering/v1p2/users/{userId}/agentFor

Builds the full path with user_id, performs the HTTP GET via the injected
`HttpClient`, and parses the response into `TimebackGetAgentForResponse`.
"""

from typing import Any, Dict

from timeback.http import HttpClient
from timeback.models.response import TimebackGetAgentForResponse
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="INFO")


def get_agent_for(http: HttpClient, user_id: str) -> TimebackGetAgentForResponse:
    """Get users this user is an agent for (e.g., parents getting children list).

    Args:
        http: Injected HTTP client for making requests
        user_id: The sourcedId of the user

    Returns:
        TimebackGetAgentForResponse containing list of users this user is an agent for
    """
    log.debug(f"User ID: {user_id}")
    data: Dict[str, Any] = http.get(
        f"/ims/oneroster/rostering/v1p2/users/{user_id}/agentFor"
    )
    log.debug(f"Raw Data: {data}")
    return TimebackGetAgentForResponse.model_validate(data)
