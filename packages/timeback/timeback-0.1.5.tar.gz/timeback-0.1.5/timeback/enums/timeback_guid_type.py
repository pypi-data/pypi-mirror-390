from enum import Enum


class TimebackGuidType(str, Enum):
    """GUID entity types used across resources.

    Mirrors DB enum "public.guid_type" in `timeback/schemas/oneroster.sql`.
    """

    ACADEMIC_SESSION = "academicSession"
    ASSESSMENT_LINE_ITEM = "assessmentLineItem"
    CATEGORY = "category"
    CLASS = "class"
    COURSE = "course"
    DEMOGRAPHICS = "demographics"
    ENROLLMENT = "enrollment"
    GRADING_PERIOD = "gradingPeriod"
    LINE_ITEM = "lineItem"
    ORG = "org"
    RESOURCE = "resource"
    RESULT = "result"
    SCORE_SCALE = "scoreScale"
    STUDENT = "student"
    TEACHER = "teacher"
    TERM = "term"
    USER = "user"
    COMPONENT_RESOURCE = "componentResource"
    COURSE_COMPONENT = "courseComponent"


