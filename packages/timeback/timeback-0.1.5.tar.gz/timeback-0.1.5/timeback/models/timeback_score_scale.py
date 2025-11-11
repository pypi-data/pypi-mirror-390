"""ScoreScale model for OneRoster API.

Matches the OneRoster 1.2 ScoreScale schema (excerpted in docs).
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from timeback.enums import TimebackStatus
from timeback.models.timeback_sourced_id_ref import TimebackSourcedIdReference


class TimebackScoreScaleValue(BaseModel):
    itemValueLHS: str
    itemValueRHS: str
    value: str
    description: Optional[str] = None


class TimebackScoreScale(BaseModel):
    sourcedId: str
    status: TimebackStatus
    dateLastModified: Optional[str] = None
    metadata: Optional[dict] = None
    title: str
    type: str
    class_: TimebackSourcedIdReference = Field(alias="class")
    course: Optional[TimebackSourcedIdReference] = None
    scoreScaleValue: List[TimebackScoreScaleValue]


