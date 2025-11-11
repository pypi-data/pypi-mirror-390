from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackScoreScaleRef(BaseModel):
    """Score scale reference."""

    sourcedId: str = Field(..., description="Unique identifier of the score scale")
    type: TimebackGuidType = Field(default=TimebackGuidType.SCORE_SCALE, description="Reference type (score_scale)")


