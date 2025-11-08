"""Resource model for the TimeBack API.

This module defines the Resource class which represents a learning resource
following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from timeback.enums import TimebackImportance, TimebackRoleType, TimebackStatus


class TimebackResource(BaseModel):
    """
    Educational resources like videos, documents, or interactive content. Resources are created with a vendorResourceId and receive an allocatedSourcedId from the system. The metadata requirements vary based on the resource type (video, audio, text, etc).
    """

    sourcedId: str
    status: TimebackStatus = Field(default=TimebackStatus.ACTIVE)
    dateLastModified: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    title: str
    roles: List[TimebackRoleType] = Field(default_factory=list)
    importance: TimebackImportance
    vendorResourceId: str
    vendorId: Optional[str] = Field(default=None)
    applicationId: Optional[str] = Field(default=None)
