"""Request model for deleting an agent for a user.

DELETE /ims/oneroster/rostering/v1p2/users/{userId}/agents/{agentSourcedId}
"""

from pydantic import BaseModel, ConfigDict, Field


class TimebackDeleteAgentRequest(BaseModel):
    """Request model for deleting an agent for a user.
    
    Attributes:
        Required:
            - user_id (str): The sourcedId of the user
            - agent_sourced_id (str): The sourcedId of the agent to delete
    """

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., description="The sourcedId of the user", alias="userId")
    agent_sourced_id: str = Field(
        ..., description="The sourcedId of the agent to delete", alias="agentSourcedId"
    )

