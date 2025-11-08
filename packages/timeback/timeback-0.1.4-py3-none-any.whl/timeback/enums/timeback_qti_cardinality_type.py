from enum import Enum

class TimebackQTICardinalityType(str, Enum):
    """QTI Cardinality Types."""

    SINGLE = "single"
    MULTIPLE = "multiple"
    ORDERED = "ordered"
    RECORD = "record"