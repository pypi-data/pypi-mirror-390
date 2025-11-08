"""Component Resource model for the TimeBack API.

This module defines the ComponentResource model which represents a resource
associated with a course component following the OneRoster 1.2 specification.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus
from timeback.models import TimebackComponentRef, TimebackResourceRef


class TimebackComponentResource(BaseModel):
    """Represents a resource associated with a course component.
    
    Required fields per OneRoster 1.2 spec:
    - sourcedId: Unique identifier for the component resource
    - courseComponent: ComponentRef (href, sourcedId, type)
    - resource: ResourceRef (href, sourcedId, type)
    - title: Display title for the component resource
    
    Optional fields:
    - status: Current status ('active' or 'tobedeleted')
    - dateLastModified: Timestamp of last modification (ISO string)
    - metadata: Additional metadata as key-value pairs
    - sortOrder: Position within siblings (defaults to 0)
    """

    # Required fields
    sourcedId: str
    courseComponent: TimebackComponentRef
    resource: TimebackResourceRef
    title: str

    # Optional fields
    status: TimebackStatus = TimebackStatus.ACTIVE
    dateLastModified: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    metadata: Optional[Dict[str, Any]] = None
    sortOrder: int = 0
