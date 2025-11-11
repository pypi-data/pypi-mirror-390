"""Response model for creating a OneRoster User.

Represents the body returned by:
- POST /ims/oneroster/rostering/v1p2/users/

Per spec: HTTP 201 with `sourcedIdPairs` mapping supplied→allocated.
"""

from pydantic import BaseModel, Field

from timeback.models import TimebackSourcedIdPairs


class TimebackCreateUserResponse(BaseModel):
    """Response model for creating a OneRoster User.

    Attributes:
        - sourcedIdPairs (TimebackSourcedIdPairs): SourcedId mapping. See TimebackSourcedIdPairs for structure.
    """

    sourcedIdPairs: TimebackSourcedIdPairs = Field(
        ..., description="Mapping from supplied to allocated sourcedId"
    )
