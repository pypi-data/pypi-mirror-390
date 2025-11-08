"""UserRef model per schemas/entities/user_ref.json."""

from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackUserRef(BaseModel):
    """Reference to a user.

    Required: href, sourcedId, type (must be 'user').
    """

    href: str = Field(..., description="URI to the user resource")
    sourcedId: str = Field(..., description="Unique identifier of the user")
    type: TimebackGuidType = Field(
        default=TimebackGuidType.USER, description="Reference type (user)"
    )


