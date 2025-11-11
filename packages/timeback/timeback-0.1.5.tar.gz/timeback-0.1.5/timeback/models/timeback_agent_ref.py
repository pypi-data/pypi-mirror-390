from pydantic import BaseModel, Field, field_validator
from timeback.enums.timeback_agent_type import TimebackAgentType


class TimebackAgentRef(BaseModel):
    """Agent reference with limited types."""

    sourcedId: str = Field(..., description="Unique identifier of the agent")
    type: str = Field(..., description="Type of agent reference")

    @field_validator("type")
    def validate_type(cls, v):
        """Validate agent type includes student, user, or parent."""
        if v not in [
            TimebackAgentType.STUDENT,
            TimebackAgentType.USER,
            TimebackAgentType.PARENT,
        ]:
            raise ValueError("Agent type must be student, user, or parent")
        return v
