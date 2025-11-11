"""Get Agents endpoint for OneRoster Rostering.

GET /ims/oneroster/rostering/v1p2/users/{userId}/agents

Builds the full path with user_id, performs the HTTP GET via the injected
`HttpClient`, and parses the response into `TimebackGetAgentsResponse`.
"""

from typing import Any, Dict

from timeback.http import HttpClient
from timeback.models.response import TimebackGetAgentsResponse
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def get_agents(http: HttpClient, user_id: str) -> TimebackGetAgentsResponse:
    """Get agent users for the specified user.

    Args:
        http: Injected HTTP client for making requests
        user_id: The sourcedId of the user

    Returns:
        TimebackGetAgentsResponse containing list of agent users
    """
    log.debug(f"User ID: {user_id}")
    data: Dict[str, Any] = http.get(
        f"/ims/oneroster/rostering/v1p2/users/{user_id}/agents"
    )
    log.debug(f"Raw Data: {data}")
    return TimebackGetAgentsResponse.model_validate(data)


