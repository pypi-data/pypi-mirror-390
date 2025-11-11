from enum import Enum


class TimebackAssessmentType(str, Enum):
    """Assessment type values for metadata."""

    BRACKETING = "bracketing"
    MANUAL = "manual"
    MAP_GROWTH = "map_growth"
    MAP_SCREENING = "map_screening"
    MAP_SCREENER = "map_screener"
    TEST_OUT = "test_out"


