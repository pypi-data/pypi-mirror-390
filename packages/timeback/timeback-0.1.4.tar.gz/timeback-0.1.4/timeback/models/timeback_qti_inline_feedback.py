"""Inline feedback configuration."""

from pydantic import BaseModel


class TimebackQTIInlineFeedback(BaseModel):
    """Inline feedback configuration."""

    outcomeIdentifier: str
    variableIdentifier: str


