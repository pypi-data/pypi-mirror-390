from enum import Enum


class TimebackAcademicSessionType(str, Enum):
    """Valid academic session types in OneRoster."""

    GRADING_PERIOD = "gradingPeriod"
    SEMESTER = "semester"
    SCHOOL_YEAR = "schoolYear"
    TERM = "term"


