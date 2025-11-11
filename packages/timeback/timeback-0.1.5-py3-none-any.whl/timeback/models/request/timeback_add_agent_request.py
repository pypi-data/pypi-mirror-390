"""Request model for adding an agent to a user.

POST /ims/oneroster/rostering/v1p2/users/{userId}/agents
"""

from pydantic import BaseModel, ConfigDict, Field


class TimebackAddAgentRequest(BaseModel):
    """Request model for adding an agent to a user.
    
    Attributes:
        Required:
            - user_id (str): The sourcedId of the user
            - agent_sourced_id (str): The sourcedId of the agent to add
    """

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., description="The sourcedId of the user", alias="userId")
    agent_sourced_id: str = Field(
        ..., description="The sourcedId of the agent to add", alias="agentSourcedId"
    )

