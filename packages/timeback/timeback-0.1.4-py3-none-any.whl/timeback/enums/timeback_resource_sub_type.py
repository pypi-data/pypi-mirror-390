from enum import Enum


class TimebackResourceSubType(str, Enum):
    """Sub-types of resources (metadata level).

    Mirrors DB enum "public.resource_sub_type" in `timeback/schemas/oneroster.sql`.
    """

    QTI_TEST = "qti-test"
    QTI_QUESTION = "qti-question"
    QTI_STIMULUS = "qti-stimulus"
    QTI_TEST_BANK = "qti-test-bank"
    UNIT = "unit"
    COURSE = "course"
    RESOURCE_COLLECTION = "resource-collection"


