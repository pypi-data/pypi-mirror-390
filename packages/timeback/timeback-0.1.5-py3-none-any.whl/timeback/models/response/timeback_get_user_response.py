"""Response model for getting a OneRoster User.

Represents the body returned by:
- GET /ims/oneroster/rostering/v1p2/users/{sourcedId}
"""

from pydantic import BaseModel, Field
from timeback.models.timeback_user import TimebackUser


class TimebackGetUserResponse(BaseModel):
    """Response model for getting a OneRoster User.
    
    Attributes:
        - user (TimebackUser): User object. See TimebackUser for structure.
    """
    
    user: TimebackUser = Field(..., description="User object")

