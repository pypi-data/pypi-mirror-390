"""Enrollment model for the TimeBack API.

This module provides a Pydantic model for working with student/teacher enrollments
in the TimeBack API following the OneRoster 1.2 specification.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus
from timeback.enums import TimebackEnrollmentRole
from timeback.models.timeback_sourced_id_ref import TimebackSourcedIdReference


class TimebackEnrollment(BaseModel):
    """
    Represents a student or teacher's enrollment in a class.

    Enrollments link users to classes with a specific role and period of time.

    Required fields per OneRoster 1.2 spec:
    - role: The role of the user in the class
    - user: Reference to the user
    - class: Reference to the class
    """

    sourcedId: str
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )
    metadata: Optional[Dict[str, Any]] = None
    role: TimebackEnrollmentRole
    primary: bool = False
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
    user: TimebackSourcedIdReference
    class_: TimebackSourcedIdReference
