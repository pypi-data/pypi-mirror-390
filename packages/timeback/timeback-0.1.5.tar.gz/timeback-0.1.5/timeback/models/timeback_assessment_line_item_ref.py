from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackAssessmentLineItemRef(BaseModel):
    """Assessment line item reference."""

    sourcedId: str = Field(..., description="Unique identifier of the assessment line item")
    type: TimebackGuidType = Field(default=TimebackGuidType.ASSESSMENT_LINE_ITEM, description="Reference type (assessment_line_item)")


