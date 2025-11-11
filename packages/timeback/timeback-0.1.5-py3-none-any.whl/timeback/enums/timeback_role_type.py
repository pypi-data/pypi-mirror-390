from enum import Enum


class TimebackRoleType(str, Enum):
    """Role types in OneRoster."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
