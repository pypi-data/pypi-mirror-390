"""Get All Users endpoint for OneRoster Rostering.

GET /ims/oneroster/rostering/v1p2/users

Builds the full path and query params, performs the HTTP GET via the injected
`HttpClient`, and parses the response into `TimebackListUsersResponse`.
"""

from typing import Any, Dict, Optional, Sequence, Union

from timeback.http import HttpClient
from timeback.models.response import TimebackGetAllUsersResponse
from timeback.services.oneroster.rostering.utils.normalize_fields import (
    normalize_fields,
)
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="INFO")


def get_all_users(
    http: HttpClient,
    *,
    fields: Optional[Union[str, Sequence[str]]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort: Optional[str] = None,
    order_by: Optional[str] = None,
    filter: Optional[str] = None,
    search: Optional[str] = None,
) -> TimebackGetAllUsersResponse:
    """Fetch a paginated list of users.

    Parameters map to OneRoster query parameters; `order_by` maps to `orderBy`.
    """
    path = "/ims/oneroster/rostering/v1p2/users"

    query: Dict[str, Any] = {}
    normalized_fields = normalize_fields(fields)
    if normalized_fields:
        query["fields"] = normalized_fields
    if limit is not None:
        query["limit"] = limit
    if offset is not None:
        query["offset"] = offset
    if sort is not None:
        query["sort"] = sort
    if order_by is not None:
        query["orderBy"] = order_by
    if filter is not None:
        query["filter"] = filter
    if search is not None:
        query["search"] = search

    data: Dict[str, Any] = http.get(path, params=query)
    log.debug(f"Raw Data: {data}")
    return TimebackGetAllUsersResponse.model_validate(data)


