"""Organization models for the TimeBack API.

This module defines the data models for organizations following the OneRoster v1.2 specification.
Organizations represent educational institutions such as departments, schools, districts,
and other administrative units in the hierarchy.

API Endpoints:
- GET /orgs - List organizations
- GET /orgs/{id} - Get a specific organization
- POST /orgs - Create a new organization
- PUT /orgs/{id} - Update an organization
- DELETE /orgs/{id} - Delete an organization (sets status to tobedeleted)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import uuid
from timeback.enums.timeback_org_type import TimebackOrgType
from timeback.enums.timeback_status import TimebackStatus
from timeback.models.timeback_org_ref import TimebackOrgRef

class TimebackOrg(BaseModel):
    """OneRoster Organization model.
    
    Required Fields:
    - name: Name of the organization
    - type: Type of organization (department, school, district, etc.)
    
    Optional Fields:
    - sourcedId: Unique identifier (auto-generated if not provided)
    - status: active or tobedeleted (defaults to active)
    - metadata: Additional custom properties
    - identifier: External identifier for the organization
    - parent: Reference to parent organization
    """
    
    # Required fields
    name: str = Field(..., description="Name of the organization")
    type: TimebackOrgType = Field(..., description="Type of organization")
    
    # Optional fields with defaults
    sourcedId: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    status: TimebackStatus = Field(default=TimebackStatus.ACTIVE, description="Organization's status")
    dateLastModified: str = Field(
        default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        description="Last modification timestamp"
    )
    
    # Optional fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    identifier: Optional[str] = Field(None, description="External identifier")
    parent: Optional[TimebackOrgRef] = Field(None, description="Reference to parent organization")
    children: List[TimebackOrgRef] = Field(default_factory=list, description="Child organizations")