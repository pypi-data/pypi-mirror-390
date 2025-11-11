from pydantic import BaseModel, Field
from timeback.enums import TimebackGuidType


class TimebackStudentRef(BaseModel):
    """Student reference."""

    sourcedId: str = Field(..., description="Unique identifier of the student")
    type: TimebackGuidType = Field(default=TimebackGuidType.STUDENT, description="Reference type (student)")


