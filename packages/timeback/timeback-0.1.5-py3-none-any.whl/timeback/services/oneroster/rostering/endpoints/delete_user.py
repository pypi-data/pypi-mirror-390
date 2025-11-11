from typing import Optional, Dict, Any
from timeback.http import HttpClient
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def delete_user(http: HttpClient, sourced_id: str) -> Optional[Dict[str, Any]]:
    """Soft delete a user (sets status to 'tobedeleted').

    DELETE /ims/oneroster/rostering/v1p2/users/{sourcedId}
    """
    log.debug(f"Deleting user: {sourced_id}")
    return http.delete(f"/ims/oneroster/rostering/v1p2/users/{sourced_id}")


