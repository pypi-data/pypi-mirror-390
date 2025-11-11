from enum import Enum


class TimebackGender(str, Enum):
    """Gender values per OneRoster dataset.

    Mirrors DB enum "public.gender" in `timeback/schemas/oneroster.sql`.
    """

    MALE = "male"
    FEMALE = "female"


