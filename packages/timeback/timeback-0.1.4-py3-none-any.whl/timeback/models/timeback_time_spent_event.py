"""Represents a student time spent activity event."""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from timeback.models.timeback_user import TimebackUser
from timeback.models.timeback_activity_context import TimebackActivityContext
from timeback.models.timeback_time_spent_metrics_collection import TimebackTimeSpentMetricsCollection


class TimebackTimeSpentEvent(BaseModel):
    """Represents a student time spent activity in the app context."""

    context: str = Field(
        "http://purl.imsglobal.org/ctx/caliper/v1p2",
        alias="@context",
        description="Caliper context URI",
    )
    id: Optional[str] = Field(
        None, description="Unique event identifier (URN:UUID) - Backend generated"
    )
    type: str = "TimeSpentEvent"
    actor: TimebackUser = Field(description="The user who spent time on the activity")
    action: str = "SpentTime"
    object: TimebackActivityContext = Field(
        description="The activity context where the event was recorded"
    )
    eventTime: str = Field(description="ISO 8601 datetime when this event occurred")
    profile: str = "TimebackProfile"
    edApp: Dict[str, Any] = Field(description="Application context info")
    generated: TimebackTimeSpentMetricsCollection = Field(
        description="Collection of time spent metrics"
    )
    target: Optional[Any] = Field(
        None, description="Entity representing a segment/location within the object"
    )
    referrer: Optional[Any] = Field(
        None, description="Entity representing the referring context"
    )
    session: Optional[Any] = Field(None, description="Current user session info")
    federatedSession: Optional[Any] = Field(
        None, description="LTI session info if applicable"
    )
    extensions: Optional[Dict[str, Any]] = Field(None, description="Additional attributes")


