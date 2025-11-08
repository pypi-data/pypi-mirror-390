from typing import Any, Dict

from timeback.models.timeback_user import TimebackUser
from timeback.errors import ParseError
from timeback.logs import logger

log = logger.configure_logging(__name__, log_level="DEBUG")


def parse_user_response(data: Dict[str, Any]) -> TimebackUser:
    """Parse user response data into TimebackUser model.
    Handles both {"user": {...}} and direct user object responses.
    """
    try:
        # Some implementations respond with {"user": {...}} while others may return the object directly
        payload = data.get("user", data)
        log.debug(f"Payload: {payload}")
        return TimebackUser.model_validate(payload)
    except Exception as e:
        raise ParseError(f"Failed to parse User response: {e}") from e
