from enum import Enum


class TimebackScoreStatus(str, Enum):
    """Valid score status values."""

    EXEMPT = "exempt"
    FULLY_GRADED = "fully graded"
    NOT_SUBMITTED = "not submitted"
    PARTIALLY_GRADED = "partially graded"
    SUBMITTED = "submitted"


