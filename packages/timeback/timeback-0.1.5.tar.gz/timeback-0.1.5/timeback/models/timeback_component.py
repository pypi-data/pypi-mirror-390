"""Component model for OneRoster API (Pydantic).

Matches `timeback/schemas/entities/component.json`.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus
from timeback.models import TimebackCourseRef, TimebackComponentRef


class TimebackComponent(BaseModel):
    """Component model according to OneRoster 1.2 specification."""

    # Required fields
    sourcedId: str
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
    title: str
    course: TimebackCourseRef

    # Optional fields
    courseComponent: Optional[TimebackComponentRef] = None
    sortOrder: Optional[int] = None
    prerequisites: Optional[List[TimebackComponentRef]] = None
    prerequisiteCriteria: Optional[str] = None
    unlockDate: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
