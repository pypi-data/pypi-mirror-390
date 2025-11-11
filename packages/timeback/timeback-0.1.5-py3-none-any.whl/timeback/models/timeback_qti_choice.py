"""Choice option for choice interactions."""

from typing import Optional
from pydantic import BaseModel


class TimebackQTIChoice(BaseModel):
    """Choice option for choice interactions."""

    identifier: str
    content: str
    feedbackInline: Optional[str] = None
    feedbackOutcomeIdentifier: Optional[str] = None


