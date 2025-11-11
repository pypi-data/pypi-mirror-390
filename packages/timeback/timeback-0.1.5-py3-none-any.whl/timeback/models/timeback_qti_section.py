"""QTI Section model."""

from typing import Optional, List
from pydantic import BaseModel, Field
from timeback.models.timeback_qti_item_ref import TimebackQTIItemRef


class TimebackQTISection(BaseModel):
    """QTI Section model."""

    identifier: str
    title: str
    visible: bool = True
    required: Optional[bool] = None
    fixed: Optional[bool] = None
    class_: Optional[List[str]] = Field(None, alias="class")
    keep_together: Optional[bool] = Field(None, alias="keep-together")
    sequence: Optional[int] = None
    qti_assessment_item_ref: Optional[List[TimebackQTIItemRef]] = Field(
        None, alias="qti-assessment-item-ref"
    )


