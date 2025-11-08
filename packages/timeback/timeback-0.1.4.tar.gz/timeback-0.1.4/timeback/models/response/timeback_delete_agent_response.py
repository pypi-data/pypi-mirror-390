from typing import Any
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class TimebackDeleteAgentResponse(BaseModel):
	"""Provider response for deleting an agent for a user.

	The provider returns a JSON object with at least a human-readable message.
	Additional keys may be present and are allowed.
	"""

	model_config = ConfigDict(extra="allow")

	message: str = Field(..., description="Confirmation message from the provider")
