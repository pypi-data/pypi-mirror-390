from enum import Enum


class TimebackEnrollmentRole(str, Enum):
    """Enrollment roles for class membership.

    Mirrors DB enum "public.enrollment_role" in `timeback/schemas/oneroster.sql`.
    """

    ADMINISTRATOR = "administrator"
    PROCTOR = "proctor"
    STUDENT = "student"
    TEACHER = "teacher"


