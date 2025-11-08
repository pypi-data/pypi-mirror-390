from typing import Optional, Sequence, Union
from timeback.http import HttpClient
from timeback.models.timeback_user import TimebackUser
from timeback.models.response import TimebackGetAllUsersResponse
from timeback.models.request import (
    TimebackUpdateUserRequest,
    TimebackCreateUserRequest,
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
from timeback.models.response import TimebackDeleteAgentResponse


class RosteringService:
    """Rostering service methods for OneRoster."""

    def __init__(self, http: HttpClient):
        self._http = http

    def get_user(
        self,
        sourced_id: str,
        fields: Optional[Union[str, Sequence[str]]] = None,
    ) -> TimebackUser:
        """Fetch a single user by sourcedId."""
        return get_user_endpoint(self._http, sourced_id, fields=fields)

    def get_all_users(
        self,
        *,
        fields: Optional[Union[str, Sequence[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        order_by: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> TimebackGetAllUsersResponse:
        """Fetch a paginated list of users."""
        return get_all_users_endpoint(
            self._http,
            fields=fields,
            limit=limit,
            offset=offset,
            sort=sort,
            order_by=order_by,
            filter=filter,
            search=search,
        )

    def update_user(
        self, sourced_id: str, request: TimebackUpdateUserRequest
    ) -> TimebackUser:
        """Update an existing user by sourcedId."""
        return update_user_endpoint(self._http, sourced_id, request)

    def create_user(self, request: TimebackCreateUserRequest) -> TimebackCreateUserResponse:
        """Create a new user."""
        return create_user_endpoint(self._http, request)

    def delete_user(self, sourced_id: str):
        """Delete (tombstone) a user by sourcedId. Returns raw provider response (None for 204)."""
        return delete_user_endpoint(self._http, sourced_id)

    def delete_agent(self, user_id: str, agent_sourced_id: str) -> Optional[TimebackDeleteAgentResponse]:
        """Delete an agent for a user. Returns typed response when provider returns a body; None for no-content."""
        return delete_agent_endpoint(self._http, user_id, agent_sourced_id)
