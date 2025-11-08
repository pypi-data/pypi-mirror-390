from typing import Dict, Any

from timeback.http import HttpClient
from timeback.models.timeback_user import TimebackUser
from timeback.models.request.timeback_update_user_request import (
    TimebackUpdateUserRequest,
)
from timeback.models.response import TimebackUpdateUserResponse
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def update_user(
    http: HttpClient, sourced_id: str, request: TimebackUpdateUserRequest
) -> TimebackUser:
    """Update an existing user.

    PUT /ims/oneroster/rostering/v1p2/users/{sourcedId}
    """
    body: Dict[str, Any] = request.to_dict()
    log.debug(f"PUT body: {body}")
    data: Dict[str, Any] = http.put(
        f"/ims/oneroster/rostering/v1p2/users/{sourced_id}", json=body
    )
    log.debug(f"Raw Data: {data}")
    # Validate via response model, then return the contained user
    resp = TimebackUpdateUserResponse.model_validate(data)
    return resp.user
