from typing import Optional, Dict, Any
from timeback.http import HttpClient
from timeback.logs import logger
from timeback.models.response import TimebackDeleteAgentResponse

log = logger.configure_logging(__name__, log_level="DEBUG")


def delete_agent(http: HttpClient, user_id: str, agent_sourced_id: str) -> Optional[TimebackDeleteAgentResponse]:
	"""Delete an agent for a user.

	DELETE /ims/oneroster/rostering/v1p2/users/{userId}/agents/{agentSourcedId}
	"""
	log.debug(f"Deleting agent '{agent_sourced_id}' for user '{user_id}'")
	data = http.delete(
		f"/ims/oneroster/rostering/v1p2/users/{user_id}/agents/{agent_sourced_id}"
	)
	if data is None:
		return None
	return TimebackDeleteAgentResponse.model_validate(data)
