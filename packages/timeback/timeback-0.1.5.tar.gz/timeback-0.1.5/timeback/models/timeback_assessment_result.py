"""OneRoster Assessment Result model with simplified references."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from timeback.enums.timeback_status import TimebackStatus
from timeback.enums.timeback_score_status import TimebackScoreStatus
from timeback.models.timeback_assessment_line_item_ref import TimebackAssessmentLineItemRef
from timeback.models.timeback_student_ref import TimebackStudentRef
from timeback.models.timeback_score_scale_ref import TimebackScoreScaleRef
from timeback.models.timeback_learning_objective_set import TimebackLearningObjectiveSet
from timeback.models.timeback_assessment_metadata import TimebackAssessmentMetadata


class TimebackAssessmentResult(BaseModel):
    """OneRoster Assessment Result model with simplified references."""

    # Required fields
    sourcedId: str = Field(..., description="Unique identifier")
    status: TimebackStatus = Field(
        default=TimebackStatus.ACTIVE, description="Assessment result's status"
    )
    assessmentLineItem: TimebackAssessmentLineItemRef = Field(
        ..., description="Reference to assessment line item"
    )
    student: TimebackStudentRef = Field(
        ..., description="Reference to the student"
    )
    scoreDate: str = Field(..., description="Date when the score was recorded")
    scoreStatus: TimebackScoreStatus = Field(
        ..., description="Status of the score"
    )

    # Optional fields
    dateLastModified: Optional[str] = Field(
        None, description="Last modification timestamp"
    )
    metadata: Optional[TimebackAssessmentMetadata] = Field(
        None, description="Custom metadata"
    )
    score: Optional[float] = Field(None, description="Numeric score value")
    textScore: Optional[str] = Field(
        None, description="Text representation of the score"
    )
    scoreScale: Optional[TimebackScoreScaleRef] = Field(
        None, description="Reference to score scale"
    )
    scorePercentile: Optional[float] = Field(
        None, description="Percentile rank of the score"
    )
    comment: Optional[str] = Field(None, description="Comment about the assessment result")
    learningObjectiveSet: Optional[List[TimebackLearningObjectiveSet]] = Field(
        None, description="Learning objective results"
    )
    inProgress: Optional[str] = Field(None, description="In progress indicator")
    incomplete: Optional[str] = Field(None, description="Incomplete indicator")
    late: Optional[str] = Field(None, description="Late submission indicator")
    missing: Optional[str] = Field(None, description="Missing submission indicator")


