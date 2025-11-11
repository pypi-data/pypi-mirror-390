## OneRoster — Rostering - Delete Agent

### DELETE /ims/oneroster/rostering/v1p2/users/{userId}/agents/{agentSourcedId}

- Method: DELETE
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Delete an agent for a user.

Request model:

- `TimebackDeleteAgentRequest` with required fields:
  - `user_id` (string) — The sourcedId of the user (used in path)
  - `agent_sourced_id` (string) — The sourcedId of the agent to delete (used in path)

Path params (extracted from request):

- `userId` (string, required): The sourcedId of the user
- `agentSourcedId` (string, required): The sourcedId of the agent to delete

Successful response (HTTP 200):

- Body: `{ "message": "Agent deleted successfully", ... }` (additional properties allowed)
- Client return type: `Optional[Dict[str, Any]]`
  - Returns a dictionary with provider response (may include `message` and other fields)
  - Returns `None` if provider returns no content (204)

Error responses:

- 400/422: Request/validation → raises `RequestError`
- 401: Unauthorized → raises `AuthError`
- 403: Forbidden → raises `RequestError`
- 404: Not Found → raises `NotFoundError`
- 429: Too Many Requests → raises `RateLimitError`
- 5xx: Server errors → raises `ServerError`

Python usage:

```python
from timeback import Timeback
from timeback.models.request import TimebackDeleteAgentRequest

client = Timeback()
request = TimebackDeleteAgentRequest(user_id="user-sourced-id", agent_sourced_id="agent-sourced-id")
result = client.oneroster.rostering.delete_agent(request)
if result is not None:
    print(result.get("message", "Agent deleted successfully"))
```
