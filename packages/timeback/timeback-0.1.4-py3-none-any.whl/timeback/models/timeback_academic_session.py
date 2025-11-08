"""AcademicSession model for OneRoster API.

This module defines the AcademicSession model according to the OneRoster 1.2 specification.
Academic sessions represent time periods like terms, semesters, grading periods, or school years
that are used to organize classes and enrollments.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid
from timeback.enums import TimebackStatus, TimebackAcademicSessionType
from timeback.models.timeback_org_ref import TimebackOrgRef


class TimebackAcademicSession(BaseModel):
    """AcademicSession model for OneRoster API.

    Required fields (per OneRoster 1.2 spec):
    - title: The title of this academic session
    - type: The type of session - gradingPeriod, semester, schoolYear, or term
    - startDate: When this session starts (ISO 8601 date)
    - endDate: When this session ends (ISO 8601 date)
    - schoolYear: The school year this session belongs to
    - org: The organization this session belongs to (reference)

    Optional fields:
    - sourcedId: The unique identifier for this academic session
    - status: 'active' or 'tobedeleted'
    - dateLastModified: When this session was last modified (ISO 8601)
    - parent: Reference to a parent academic session
    - metadata: Additional properties not defined in the spec
    """

    # Optional identifier with default factory
    sourcedId: Optional[str] = Field(
        default_factory=lambda: f"academicSession-{str(uuid.uuid4())}",
        description="Unique identifier for this session",
    )

    # Required core fields
    title: str
    type: TimebackAcademicSessionType
    startDate: str
    endDate: str
    schoolYear: int
    org: TimebackOrgRef

    # Optional fields with defaults
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        description="Last modification timestamp",
    )

    # Optional fields
    parent: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
