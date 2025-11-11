"""Set of learning objective results."""

from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_learning_objective_result import TimebackLearningObjectiveResult


class TimebackLearningObjectiveSet(BaseModel):
    """Set of learning objective results."""

    source: str = Field(..., description="Source of the learning objectives")
    learningObjectiveResults: List[TimebackLearningObjectiveResult] = Field(
        ..., description="Results for individual learning objectives"
    )


