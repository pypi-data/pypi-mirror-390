from pydantic import BaseModel


class TimebackUserId(BaseModel):
    """External user identifier."""

    type: str
    identifier: str
