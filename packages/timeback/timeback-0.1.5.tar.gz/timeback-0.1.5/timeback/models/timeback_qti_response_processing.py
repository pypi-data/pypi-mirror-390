"""Response processing for assessment items."""

from typing import Optional
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_inline_feedback import TimebackQTIInlineFeedback


class TimebackQTIResponseProcessing(BaseModel):
    """Response processing for assessment items."""

    templateType: str
    responseDeclarationIdentifier: str
    outcomeIdentifier: str
    correctResponseIdentifier: Optional[str] = None
    incorrectResponseIdentifier: Optional[str] = None
    inlineFeedback: Optional[TimebackQTIInlineFeedback] = None


