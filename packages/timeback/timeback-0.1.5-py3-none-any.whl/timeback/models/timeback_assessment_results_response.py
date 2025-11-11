"""Response model for paginated assessment results list."""

from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_assessment_result import TimebackAssessmentResult


class TimebackAssessmentResultsResponse(BaseModel):
    """Response model for paginated assessment results list."""

    assessmentResults: List[TimebackAssessmentResult] = Field(
        ..., description="List of assessment results"
    )
    totalCount: int = Field(..., description="Total number of results")
    pageCount: int = Field(..., description="Total number of pages")
    pageNumber: int = Field(..., description="Current page number")
    offset: int = Field(..., description="Offset for pagination")
    limit: int = Field(..., description="Limit per page")


