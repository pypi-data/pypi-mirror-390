"""Feedback block for assessment items."""

from pydantic import BaseModel


class TimebackQTIFeedbackBlock(BaseModel):
    """Feedback block for assessment items."""

    outcomeIdentifier: str
    identifier: str
    showHide: str = "show"
    content: str


