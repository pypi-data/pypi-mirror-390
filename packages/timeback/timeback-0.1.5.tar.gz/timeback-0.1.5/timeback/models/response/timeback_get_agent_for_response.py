from typing import List
from pydantic import BaseModel, Field
from timeback.models.timeback_agent import TimebackAgent


class TimebackGetAgentForResponse(BaseModel):
    """Response model for users that a given user is an agent for.

    Mirrors OneRoster response envelope for agentFor endpoint as documented in
    `timeback/docs/oneroster/rostering/get_agent_for.md`.
    
    Attributes:
        - users (List[TimebackAgent]): List of users this user is an agent for.
          See TimebackAgent for structure.
    """

    users: List[TimebackAgent] = Field(
        ..., description="List of users this user is an agent for"
    )
