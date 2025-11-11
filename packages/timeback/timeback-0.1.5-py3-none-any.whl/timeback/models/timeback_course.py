"""Course model for OneRoster API (Pydantic).

Matches `timeback/schemas/entities/course.json`.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus
from .timeback_resource_ref import TimebackResourceRef
from .timeback_component_ref import TimebackComponentRef


class TimebackCourse(BaseModel):
    """Course model according to OneRoster 1.2 specification."""

    # Required fields
    sourcedId: str
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
    title: str
    orgSourcedId: str

    # Optional fields
    metadata: Optional[Dict[str, Any]] = None
    courseCode: Optional[str] = None
    grades: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    subjectCodes: Optional[List[str]] = None
    resources: Optional[List[TimebackResourceRef]] = None
    components: Optional[List[TimebackComponentRef]] = None
    description: Optional[str] = None
    displayName: Optional[str] = None
