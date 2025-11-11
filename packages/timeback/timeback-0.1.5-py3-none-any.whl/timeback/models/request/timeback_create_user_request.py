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
    """Body payload for user creation under the top-level 'user' key.
    
    Attributes:
        Required:
            - enabledUser (bool | str): Whether user has system access
            - givenName (str): First name
            - familyName (str): Last name
            - roles (List[TimebackUserRole]): User roles (min 1). See TimebackUserRole for structure.
            - email (str): Unique email address
        
        Optional:
            - sourcedId (str, optional): Client-supplied sourcedId (auto-generated UUID if omitted)
            - metadata (Dict[str, Any], optional): Custom metadata
            - status (TimebackStatus, optional): User status. See TimebackStatus enum.
            - userMasterIdentifier (str, optional)
            - username (str, optional)
            - userIds (List[TimebackUserId], optional): See TimebackUserId for structure.
            - middleName (str, optional)
            - primaryOrg (TimebackOrgRef, optional): See TimebackOrgRef for structure.
            - preferredFirstName (str, optional)
            - preferredMiddleName (str, optional)
            - preferredLastName (str, optional)
            - pronouns (str, optional)
            - grades (List[str], optional)
            - password (str, optional)
            - sms (str, optional)
            - phone (str, optional)
            - agents (List[TimebackAgentRef], optional): See TimebackAgentRef for structure.
    """
    
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
    """Top-level request wrapper for POST /users/.
    
    Attributes:
        Required:
            - user (TimebackCreateUserBody): User data to create. See TimebackCreateUserBody for structure.
    """
    
    user: TimebackCreateUserBody

    def to_dict(self) -> Dict[str, Any]:
        return {"user": self.user.model_dump(exclude_none=True)}
