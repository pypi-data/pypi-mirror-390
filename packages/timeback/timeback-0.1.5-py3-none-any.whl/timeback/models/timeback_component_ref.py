"""ComponentRef model per schemas/entities/component_ref.json."""

from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackComponentRef(BaseModel):
    """Reference to a course component.

    Required: href, sourcedId, type (courseComponent)
    """

    href: str = Field(..., description="URI to the component resource")
    sourcedId: str = Field(..., description="Unique identifier of the component")
    type: TimebackGuidType = Field(
        default=TimebackGuidType.COURSE_COMPONENT, description="Reference type (courseComponent)"
    )


