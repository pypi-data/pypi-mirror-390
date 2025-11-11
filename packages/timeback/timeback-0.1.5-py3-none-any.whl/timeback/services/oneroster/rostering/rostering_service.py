from typing import Any, Dict, Optional
from timeback.http import HttpClient
from timeback.models.response import (
    TimebackGetAllUsersResponse,
    TimebackUpdateUserResponse,
    TimebackGetUserResponse,
)
from timeback.models.request import (
    TimebackUpdateUserRequest,
    TimebackCreateUserRequest,
    TimebackAddAgentRequest,
    TimebackDeleteAgentRequest,
    TimebackGetUserRequest,
    TimebackGetAllUsersRequest,
)
from timeback.models.response import TimebackCreateUserResponse
from timeback.services.oneroster.rostering.endpoints.get_user import (
    get_user as get_user_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.get_all_users import (
    get_all_users as get_all_users_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.update_user import (
    update_user as update_user_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.create_user import (
    create_user as create_user_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.delete_user import (
    delete_user as delete_user_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.delete_agent import (
    delete_agent as delete_agent_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.get_agent_for import (
    get_agent_for as get_agent_for_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.get_agents import (
    get_agents as get_agents_endpoint,
)
from timeback.services.oneroster.rostering.endpoints.add_agent import (
    add_agent as add_agent_endpoint,
)
from timeback.models.response import TimebackGetAgentForResponse
from timeback.models.response import TimebackGetAgentsResponse


class RosteringService:
    """Rostering service methods for OneRoster."""

    def __init__(self, http: HttpClient):
        self._http = http

    def get_user(self, request: TimebackGetUserRequest) -> TimebackGetUserResponse:
        """Fetch a single user by sourcedId."""
        return get_user_endpoint(self._http, request)

    def get_all_users(
        self,
        request: TimebackGetAllUsersRequest,
    ) -> TimebackGetAllUsersResponse:
        """Fetch a paginated list of users."""
        return get_all_users_endpoint(self._http, request)

    def update_user(
        self, request: TimebackUpdateUserRequest
    ) -> TimebackUpdateUserResponse:
        """Update an existing user by sourcedId."""
        return update_user_endpoint(self._http, request)

    def create_user(self, request: TimebackCreateUserRequest) -> TimebackCreateUserResponse:
        """Create a new user."""
        return create_user_endpoint(self._http, request)

    def delete_user(self, sourced_id: str):
        """Delete (tombstone) a user by sourcedId. Returns raw provider response (None for 204)."""
        return delete_user_endpoint(self._http, sourced_id)

    def delete_agent(self, request: TimebackDeleteAgentRequest) -> Optional[Dict[str, Any]]:
        """Delete an agent for a user. Returns raw provider response (None for no-content)."""
        return delete_agent_endpoint(self._http, request)

    def get_agent_for(self, user_id: str) -> TimebackGetAgentForResponse:
        """Get users this user is an agent for (e.g., parents getting children list)."""
        return get_agent_for_endpoint(self._http, user_id)

    def get_agents(self, user_id: str) -> TimebackGetAgentsResponse:
        """Get agent users for the specified user."""
        return get_agents_endpoint(self._http, user_id)

    def add_agent(self, request: TimebackAddAgentRequest) -> Dict[str, Any]:
        """Add an agent for a user. Returns raw provider response."""
        return add_agent_endpoint(self._http, request)
