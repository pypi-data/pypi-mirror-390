from typing import List

from pydantic import BaseModel, Field

from timeback.models import TimebackAgent


class TimebackGetAgentsResponse(BaseModel):
    """Response model for agents of a given user.

    Mirrors OneRoster response envelope for the agents endpoint:
    { "agents": [User, ...] }
    
    Attributes:
        - agents (List[TimebackAgent]): List of agent users associated with the given user.
          See TimebackAgent for structure.
    """

    agents: List[TimebackAgent] = Field(
        ..., description="List of agent users associated with the given user"
    )
