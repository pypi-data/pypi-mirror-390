"""Represents a time spent metric for a segment of activity."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from timeback.enums.timeback_time_spent_type import TimebackTimeSpentType


class TimebackTimeSpentMetric(BaseModel):
    """Represents a time spent metric for a segment of activity."""

    type: TimebackTimeSpentType = Field(description="Type of time spent (active, inactive, waste)")
    subType: Optional[str] = Field(None, description="Subtype for more specific activity representation")
    value: float = Field(description="Duration in seconds")
    startDate: Optional[str] = Field(None, description="ISO 8601 start timestamp")
    endDate: Optional[str] = Field(None, description="ISO 8601 end timestamp")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")


