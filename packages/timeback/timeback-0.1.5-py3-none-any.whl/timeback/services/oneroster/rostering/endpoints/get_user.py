from typing import Any, Dict

from timeback.http import HttpClient
from timeback.models.response import TimebackGetUserResponse
from timeback.models.request import TimebackGetUserRequest
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="INFO")


def get_user(http: HttpClient, request: TimebackGetUserRequest) -> TimebackGetUserResponse:
    """Fetch a single user by sourcedId.

    GET /ims/oneroster/rostering/v1p2/users/{sourcedId}

    Args:
        http: Injected HTTP client for making requests
        request: Request containing sourced_id and optional query parameters

    Returns:
        TimebackGetUserResponse containing the user data
    """
    log.debug(f"Request: {request}")
    # Extract query params if provided
    params: Dict[str, Any] = {}
    if request.query_params:
        params = request.query_params.to_query_dict()
    log.debug(f"Params: {params}")
    log.debug(f"Sourced ID: {request.sourced_id}")
    data = http.get(
        f"/ims/oneroster/rostering/v1p2/users/{request.sourced_id}", params=params
    )
    log.debug(f"Raw Data: {data}")
    return TimebackGetUserResponse.model_validate(data)
