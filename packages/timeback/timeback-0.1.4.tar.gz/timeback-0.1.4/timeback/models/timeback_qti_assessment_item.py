"""QTI Assessment Item model to match the API expectations."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_interaction import TimebackQTIInteraction
from timeback.models.timeback_qti_response_declaration import (
    TimebackQTIResponseDeclaration,
)
from timeback.models.timeback_qti_outcome_declaration import (
    TimebackQTIOutcomeDeclaration,
)
from timeback.models.timeback_qti_response_processing import (
    TimebackQTIResponseProcessing,
)
from timeback.models.timeback_qti_feedback_block import TimebackQTIFeedbackBlock
from timeback.models.timeback_qti_rubric import TimebackQTIRubric
from timeback.models.timeback_qti_stimulus import TimebackQTIStimulus
from timeback.models.timeback_qti_item_body import TimebackQTIItemBody


class TimebackQTIAssessmentItem(BaseModel):
    """QTI Assessment Item model to match the API expectations."""

    identifier: str
    title: Optional[str] = None
    type: Optional[str] = None
    preInteraction: Optional[str] = None
    postInteraction: Optional[str] = None
    interaction: Optional[TimebackQTIInteraction] = None
    responseDeclarations: Optional[List[TimebackQTIResponseDeclaration]] = None
    outcomeDeclarations: Optional[List[TimebackQTIOutcomeDeclaration]] = None
    responseProcessing: Optional[TimebackQTIResponseProcessing] = None
    feedbackBlock: Optional[List[TimebackQTIFeedbackBlock]] = None
    rubrics: Optional[List[TimebackQTIRubric]] = None
    stimulus: Optional[TimebackQTIStimulus] = None
    metadata: Optional[Dict[str, Any]] = None

    adaptive: Optional[bool] = None
    timeDependent: Optional[bool] = None
    itemBody: Optional[TimebackQTIItemBody] = None
    content: Optional[Any] = None
    rawXml: Optional[str] = None
    qtiVersion: Optional[str] = Field(None, description="Version of QTI standard (default: '3.0')")


