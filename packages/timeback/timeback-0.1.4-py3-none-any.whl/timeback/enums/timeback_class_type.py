from enum import Enum


class TimebackClassType(str, Enum):
    """Class type values."""

    HOMEROOM = "homeroom"
    SCHEDULED = "scheduled"
