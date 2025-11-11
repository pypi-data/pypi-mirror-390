from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from timeback.enums import TimebackStatus
from timeback.models.timeback_user_id import TimebackUserId
from timeback.models.timeback_org_ref import TimebackOrgRef

class TimebackAgent(BaseModel):
    """Simplified user model for agents endpoint response.

    This model matches the actual API response format which may:
    - Return primaryOrg as a string (sourcedId) instead of an object
    - Include additional fields like tenantId, clientAppId, identifier, isTestUser
    """

    # Required fields from API
    tenantId: Optional[str] = Field(None, description="Tenant identifier")
    clientAppId: Optional[str] = Field(
        None, description="Client application identifier"
    )
    sourcedId: str = Field(..., description="Unique identifier")
    status: TimebackStatus = Field(
        default=TimebackStatus.ACTIVE, description="User's status"
    )
    dateLastModified: Optional[str] = Field(
        None, description="Last modification timestamp"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    username: Optional[str] = Field(None, description="Legacy username")
    enabledUser: bool = Field(..., description="Whether user has system access")
    givenName: str = Field(..., description="First name")
    familyName: str = Field(..., description="Last name")
    middleName: Optional[str] = Field(None, description="Middle name")
    identifier: Optional[str] = Field(None, description="User identifier")
    email: Optional[str] = Field(None, description="Email address")
    sms: Optional[str] = Field(None, description="SMS number")
    phone: Optional[str] = Field(None, description="Phone number")
    password: Optional[str] = Field(None, description="User password")
    grades: Optional[List[str]] = Field(None, description="Grade levels")
    userIds: Optional[List[TimebackUserId]] = Field(
        None, description="External system identifiers"
    )
    userMasterIdentifier: Optional[str] = Field(
        None, description="Master identifier across systems"
    )
    preferredFirstName: Optional[str] = Field(None, description="Preferred first name")
    preferredMiddleName: Optional[str] = Field(
        None, description="Preferred middle name"
    )
    preferredLastName: Optional[str] = Field(None, description="Preferred last name")
    pronouns: Optional[str] = Field(None, description="Preferred pronouns")
    primaryOrg: Optional[Union[str, TimebackOrgRef]] = Field(
        None, description="Primary organization (may be sourcedId string or object)"
    )
    isTestUser: Optional[bool] = Field(None, description="Whether this is a test user")
    roles: Optional[List[Any]] = Field(
        None, description="User's roles and organizations"
    )

    @field_validator("dateLastModified", mode="before")
    def convert_dateLastModified(cls, v):
        """Convert datetime dateLastModified to ISO string."""
        if isinstance(v, datetime):
            return v.isoformat() + "Z"
        return v