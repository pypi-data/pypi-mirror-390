from enum import Enum


class TimebackStatus(str, Enum):
    """Universal status values."""

    ACTIVE = "active"
    TOBEDELETED = "tobedeleted"
