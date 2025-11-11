from enum import Enum


class TimebackResourceType(str, Enum):
    """Top-level resource types.

    Mirrors DB enum "public.resource_type" in `timeback/schemas/oneroster.sql`.
    """

    QTI = "qti"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    INTERACTIVE = "interactive"
    VISUAL = "visual"
    COURSE_MATERIAL = "course-material"


