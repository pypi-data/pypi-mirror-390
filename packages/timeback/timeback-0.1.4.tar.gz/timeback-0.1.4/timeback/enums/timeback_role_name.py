from enum import Enum


class TimebackRoleName(str, Enum):
    """Valid user roles in the TimeBack API."""

    ADMINISTRATOR = "administrator"
    AIDE = "aide"
    GUARDIAN = "guardian"
    PARENT = "parent"
    PROCTOR = "proctor"
    RELATIVE = "relative"
    STUDENT = "student"
    TEACHER = "teacher"
