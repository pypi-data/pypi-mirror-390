"""Request model for updating a OneRoster User.

This request mirrors the body for:
- PUT /ims/oneroster/rostering/v1p2/users/{sourcedId}

The payload follows the OneRoster v1.2 spec with Timeback enums/models.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator

from timeback.enums import TimebackStatus
from timeback.models.timeback_user_role import TimebackUserRole
from timeback.models.timeback_user_id import TimebackUserId
from timeback.models.timeback_agent_ref import TimebackAgentRef
from timeback.models.timeback_org_ref import TimebackOrgRef


class TimebackUpdateUserBody(BaseModel):
    """Body payload for user update under the top-level 'user' key."""

    # Required fields per spec
    enabledUser: Union[bool, str] = Field(..., description="Whether user has system access")
    givenName: str = Field(..., description="First name")
    familyName: str = Field(..., description="Last name")
    roles: List[TimebackUserRole] = Field(..., description="User roles (min 1)")
    email: str = Field(..., description="Unique email address")

    # Optional
    sourcedId: Optional[str] = Field(None, description="User sourcedId (id in path is authoritative)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
    status: Optional[TimebackStatus] = Field(None, description="User status")
    userMasterIdentifier: Optional[str] = None
    username: Optional[str] = None
    userIds: Optional[List[TimebackUserId]] = None
    middleName: Optional[str] = None
    primaryOrg: Optional[TimebackOrgRef] = None
    preferredFirstName: Optional[str] = None
    preferredMiddleName: Optional[str] = None
    preferredLastName: Optional[str] = None
    pronouns: Optional[str] = None
    grades: Optional[List[str]] = None
    password: Optional[str] = None
    sms: Optional[str] = None
    phone: Optional[str] = None
    agents: Optional[List[TimebackAgentRef]] = Field(default=None, description="Agent references")

    @field_validator("enabledUser", mode="before")
    @classmethod
    def normalize_enabled_user(cls, v: Union[bool, str]) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)


class TimebackUpdateUserRequest(BaseModel):
    """Top-level request wrapper for PUT /users/{sourcedId}."""

    user: TimebackUpdateUserBody

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to API-compatible dictionary."""
        return {"user": self.user.model_dump(exclude_none=True)}


