from enum import Enum


class TimebackClientAppStatus(str, Enum):
    """Status for client applications.

    Mirrors DB enum "public.client_app_status" in `timeback/schemas/oneroster.sql`.
    """

    ENABLED = "enabled"
    DISABLED = "disabled"


