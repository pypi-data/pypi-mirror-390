"""ResourceRef model per schemas/entities/resource_ref.json."""

from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackResourceRef(BaseModel):
    """Reference to a resource.

    Required: href, sourcedId, type (must be 'resource').
    """

    href: str = Field(..., description="URI to the resource")
    sourcedId: str = Field(..., description="Unique identifier of the resource")
    type: TimebackGuidType = Field(
        default=TimebackGuidType.RESOURCE, description="Reference type (resource)"
    )


