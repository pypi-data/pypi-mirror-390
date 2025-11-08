from timeback.enums.timeback_role_type import TimebackRoleType
from timeback.enums.timeback_role_name import TimebackRoleName
from timeback.models.timeback_org_ref import TimebackOrgRef
from pydantic import BaseModel
from typing import Optional


class TimebackUserRole(BaseModel):
    """Role assignment with organization reference."""

    roleType: TimebackRoleType
    role: TimebackRoleName
    org: TimebackOrgRef
    userProfile: Optional[str] = None
    beginDate: Optional[str] = None
    endDate: Optional[str] = None
