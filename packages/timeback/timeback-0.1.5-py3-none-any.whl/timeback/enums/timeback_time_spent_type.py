from enum import Enum


class TimebackTimeSpentType(str, Enum):
    """Type of time spent metric (active, inactive, waste)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    WASTE = "waste"


