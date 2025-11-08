"""Request model for creating a OneRoster User.

POST /ims/oneroster/rostering/v1p2/users/
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4
from timeback.enums import TimebackStatus
from timeback.models.timeback_user_role import TimebackUserRole
from timeback.models.timeback_user_id import TimebackUserId
from timeback.models.timeback_agent_ref import TimebackAgentRef
from timeback.models.timeback_org_ref import TimebackOrgRef


class TimebackCreateUserBody(BaseModel):
    # Optional client-supplied sourcedId; if omitted, auto-generate a UUID string
    sourcedId: Optional[str] = Field(default_factory=lambda: str(uuid4()))
    enabledUser: Union[bool, str] = Field(...)
    givenName: str = Field(...)
    familyName: str = Field(...)
    roles: List[TimebackUserRole] = Field(...)
    email: str = Field(...)

    # Optional fields similar to update
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[TimebackStatus] = None
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
    agents: Optional[List[TimebackAgentRef]] = None

    @field_validator("enabledUser", mode="before")
    @classmethod
    def normalize_enabled_user(cls, v: Union[bool, str]) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)


class TimebackCreateUserRequest(BaseModel):
    user: TimebackCreateUserBody

    def to_dict(self) -> Dict[str, Any]:
        return {"user": self.user.model_dump(exclude_none=True)}
