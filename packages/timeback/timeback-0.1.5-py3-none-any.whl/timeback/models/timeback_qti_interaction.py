"""QTI Interaction that defines the interaction type and properties."""

from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from timeback.enums import TimebackQuestionType
from timeback.models.timeback_qti_object_attributes import TimebackQTIObjectAttributes
from timeback.models.timeback_qti_question_structure import TimebackQTIQuestionStructure


class TimebackQTIInteraction(BaseModel):
    """QTI Interaction that defines the interaction type and properties."""

    type: TimebackQuestionType
    responseIdentifier: str
    prompt: Optional[str] = None
    shuffle: Optional[bool] = None
    maxChoices: Optional[int] = None
    minChoices: Optional[int] = None
    maxAssociations: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    questionStructure: Optional[Union[TimebackQTIQuestionStructure, Dict[str, Any]]] = (
        None
    )

    # Graphic/Media interaction properties
    object: Optional[TimebackQTIObjectAttributes] = None

    # Slider-specific properties
    lower_bound: Optional[float] = Field(None, alias="lower-bound")
    upper_bound: Optional[float] = Field(None, alias="upper-bound")
    step: Optional[float] = None
    step_label: Optional[bool] = Field(None, alias="step-label")
    orientation: Optional[str] = None
    reverse: Optional[bool] = None

    # Media-specific properties
    minPlays: Optional[int] = None
    maxPlays: Optional[int] = None
    autostart: Optional[bool] = None
    loop: Optional[bool] = None
