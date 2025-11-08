"""Response model for creating a OneRoster User.

Represents the body returned by:
- POST /ims/oneroster/rostering/v1p2/users/

Per spec: HTTP 201 with `sourcedIdPairs` mapping supplied→allocated.
"""

from pydantic import BaseModel, Field


class TimebackSourcedIdPairs(BaseModel):
    suppliedSourcedId: str = Field(..., description="Client-supplied sourcedId")
    allocatedSourcedId: str = Field(..., description="Server-allocated sourcedId")


class TimebackCreateUserResponse(BaseModel):
    sourcedIdPairs: TimebackSourcedIdPairs = Field(
        ..., description="Mapping from supplied to allocated sourcedId"
    )


