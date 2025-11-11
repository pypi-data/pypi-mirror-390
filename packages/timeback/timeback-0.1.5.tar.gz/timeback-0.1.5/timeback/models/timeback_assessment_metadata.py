"""Assessment metadata structure."""

from typing import Optional
from pydantic import BaseModel, Field
from timeback.enums.timeback_assessment_type import TimebackAssessmentType


class TimebackAssessmentMetadata(BaseModel):
    """Assessment metadata structure."""

    model_config = {"extra": "allow"}

    studentEmail: Optional[str] = Field(None, description="Student's email address")
    assignmentId: Optional[str] = Field(None, description="Assignment identifier")
    assessmentType: Optional[TimebackAssessmentType] = Field(
        None, description="Type of assessment"
    )
    subject: Optional[str] = Field(None, description="Subject of the assessment")
    grade: Optional[float] = Field(None, description="Numeric grade representation")
    testname: Optional[str] = Field(None, description="Name of the test from metadata")


