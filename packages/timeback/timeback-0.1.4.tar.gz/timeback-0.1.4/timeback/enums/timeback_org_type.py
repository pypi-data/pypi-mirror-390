from enum import Enum


class TimebackOrgType(str, Enum):
    """Valid organization types in the TimeBack API."""

    DEPARTMENT = "department"
    SCHOOL = "school"
    DISTRICT = "district"
    LOCAL = "local"
    STATE = "state"
    NATIONAL = "national"


