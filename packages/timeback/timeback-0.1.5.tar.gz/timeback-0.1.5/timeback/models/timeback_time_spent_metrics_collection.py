"""Collection of time spent metrics for a single event."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from timeback.models.timeback_time_spent_metric import TimebackTimeSpentMetric


class TimebackTimeSpentMetricsCollection(BaseModel):
    """Collection of time spent metrics for a single event."""

    id: Optional[str] = Field(None, description="Unique identifier for the collection (URI) - Backend generated")
    type: str = "TimebackTimeSpentMetricsCollection"
    items: List[TimebackTimeSpentMetric] = Field(description="List of time spent metrics")
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")


