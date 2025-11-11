from typing import Dict, Any

from timeback.http import HttpClient
from timeback.models.request.timeback_update_user_request import (
    TimebackUpdateUserRequest,
)
from timeback.models.response import TimebackUpdateUserResponse
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def update_user(
    http: HttpClient, request: TimebackUpdateUserRequest
) -> TimebackUpdateUserResponse:
    """Update an existing user.

    PUT /ims/oneroster/rostering/v1p2/users/{sourcedId}

    Args:
        http: Injected HTTP client for making requests
        request: Request containing user data with sourcedId

    Returns:
        TimebackUpdateUserResponse containing the updated user
    """
    log.debug(f"Request: {request}")
    body: Dict[str, Any] = request.to_dict()
    log.debug(f"PUT body: {body}")
    # Extract sourcedId from body for path parameter
    sourced_id = request.user.sourcedId
    data: Dict[str, Any] = http.put(
        f"/ims/oneroster/rostering/v1p2/users/{sourced_id}", json=body
    )
    log.debug(f"Raw Data: {data}")
    return TimebackUpdateUserResponse.model_validate(data)
