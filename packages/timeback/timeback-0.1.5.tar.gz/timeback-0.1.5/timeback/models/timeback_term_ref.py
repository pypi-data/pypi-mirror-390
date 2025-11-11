"""TermRef model per schemas/entities/term_ref.json."""

from pydantic import BaseModel, Field


class TimebackTermRef(BaseModel):
    """Reference to an academic term/session.

    Required: sourcedId.
    """

    sourcedId: str = Field(..., description="Unique identifier of the term/session")


