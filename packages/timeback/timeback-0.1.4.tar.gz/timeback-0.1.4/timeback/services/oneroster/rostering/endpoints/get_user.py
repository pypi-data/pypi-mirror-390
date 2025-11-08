from typing import Any, Dict, Optional, Sequence, Union

from timeback.http import HttpClient
from timeback.models.timeback_user import TimebackUser
from timeback.services.oneroster.rostering.utils.parse_user_response import (
    parse_user_response,
)
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="INFO")


def get_user(
    http: HttpClient,
    sourced_id: str,
    fields: Optional[Union[str, Sequence[str]]] = None,
) -> TimebackUser:
    """Fetch a single user by sourcedId.

    Optional query params:
    - fields: comma-separated list or sequence of field names to include
    """
    params: Dict[str, Any] = {}
    if fields:
        params["fields"] = (
            ",".join(fields) if isinstance(fields, (list, tuple)) else fields
        )
    log.debug(f"Params: {params}")
    log.debug(f"Sourced ID: {sourced_id}")
    data = http.get(f"/ims/oneroster/rostering/v1p2/users/{sourced_id}", params=params)
    log.debug(f"Raw Data: {data}")
    return parse_user_response(data)
