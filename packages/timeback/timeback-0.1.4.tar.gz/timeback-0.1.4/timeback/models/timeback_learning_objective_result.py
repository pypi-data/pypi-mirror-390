"""Individual learning objective result."""

from typing import Optional
from pydantic import BaseModel, Field


class TimebackLearningObjectiveResult(BaseModel):
    """Individual learning objective result."""

    learningObjectiveId: str = Field(..., description="ID of the learning objective")
    score: Optional[float] = Field(None, description="Numeric score for this objective")
    textScore: Optional[str] = Field(None, description="Text representation of the score")


