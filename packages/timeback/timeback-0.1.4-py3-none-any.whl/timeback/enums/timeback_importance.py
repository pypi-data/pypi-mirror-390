from enum import Enum


class TimebackImportance(str, Enum):
    """Importance ranking for related entities.

    Mirrors DB enum "public.importance" in `timeback/schemas/oneroster.sql`.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"


