"""Response model for updating a OneRoster User.

Represents the body returned by:
- PUT /ims/oneroster/rostering/v1p2/users/{sourcedId}
"""

from pydantic import BaseModel, Field
from timeback.models.timeback_user import TimebackUser


class TimebackUpdateUserResponse(BaseModel):
    """Response model for updating a OneRoster User.
    
    Attributes:
        - user (TimebackUser): Updated user object. See TimebackUser for structure.
    """
    
    user: TimebackUser = Field(..., description="Updated user object")


