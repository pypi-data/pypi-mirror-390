"""Get All Users endpoint for OneRoster Rostering.

GET /ims/oneroster/rostering/v1p2/users

Builds the full path and query params, performs the HTTP GET via the injected
`HttpClient`, and parses the response into `TimebackGetAllUsersResponse`.
"""

from typing import Any, Dict

from timeback.http import HttpClient
from timeback.models.response import TimebackGetAllUsersResponse
from timeback.models.request import TimebackGetAllUsersRequest
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="INFO")


def get_all_users(
    http: HttpClient,
    request: TimebackGetAllUsersRequest,
) -> TimebackGetAllUsersResponse:
    """Fetch a paginated list of users.

    GET /ims/oneroster/rostering/v1p2/users

    Args:
        http: Injected HTTP client for making requests
        request: Request containing optional query parameters

    Returns:
        TimebackGetAllUsersResponse containing paginated list of users
    """
    path = "/ims/oneroster/rostering/v1p2/users"

    query: Dict[str, Any] = {}
    if request.query_params:
        query = request.query_params.to_query_dict()

    data: Dict[str, Any] = http.get(path, params=query)
    log.debug(f"Raw Data: {data}")
    return TimebackGetAllUsersResponse.model_validate(data)


