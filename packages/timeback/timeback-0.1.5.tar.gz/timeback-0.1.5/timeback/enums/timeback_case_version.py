from enum import Enum


class TimebackCaseVersion(str, Enum):
    """CASE version identifiers.

    Mirrors DB enum "public.case_version" in `timeback/schemas/oneroster.sql`.
    """

    V1_1 = "1.1"


