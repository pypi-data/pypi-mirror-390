"""ResourceRef model per schemas/entities/resource_ref.json."""

from pydantic import BaseModel, Field


class TimebackSourcedIdReference(BaseModel):
    """Reference to a sourcedId.
    This is not part of the OneRoster specification. The Timeback API sometimes references only the sourcedId, not the full reference object as defined by their schema. This is used in those cases to provide type safety and validation.
    """

    sourcedId: str = Field(..., description="Unique identifier of the sourcedId")
