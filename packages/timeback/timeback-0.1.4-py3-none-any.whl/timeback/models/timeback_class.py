"""Class model for the TimeBack API.

This module provides a Pydantic model for working with classes
in the TimeBack API following the OneRoster 1.2 specification.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus, TimebackClassType
from timeback.models import (
    TimebackCourseRef,
    TimebackOrgRef,
    TimebackTermRef,
    TimebackSourcedIdReference,
)


class TimebackClass(BaseModel):
    """
    Represents a class (specific instance of a course) in the system.

    A class represents a specific section or instance of a course, typically
    for a particular term/semester. Classes are what students actually
    enroll in, rather than enrolling in courses directly.

    Required fields per OneRoster 1.2 spec:
    - title: Name of the class
    - course: Reference to the parent course
    - org: Reference to the organization (school)
    - terms: References to academic terms
    """

    sourcedId: str
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
    metadata: Optional[Dict[str, Any]] = None
    title: str
    classCode: Optional[str] = None
    classType: Optional[TimebackClassType] = None
    location: Optional[str] = None
    grades: Optional[List[str]] = None
    subjects: Optional[List[str]] = None
    course: TimebackCourseRef
    org: TimebackOrgRef
    subjectCodes: Optional[List[str]] = None
    periods: Optional[List[str]] = None
    resources: Optional[List[TimebackSourcedIdReference]] = None
    terms: List[TimebackTermRef]
