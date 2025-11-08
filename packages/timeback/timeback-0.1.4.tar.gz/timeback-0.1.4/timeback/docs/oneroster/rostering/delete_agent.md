## OneRoster — Rostering - Delete Agent

### DELETE /ims/oneroster/rostering/v1p2/users/{userId}/agents/{agentSourcedId}

- Method: DELETE
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Delete an agent for a user.

Path params:

- `userId` (string, required): The sourcedId of the user
- `agentSourcedId` (string, required): The sourcedId of the agent to delete

Successful response (HTTP 200):

- Body: `{ "message": "Agent deleted successfully" }`
- Client return type: `TimebackDeleteAgentResponse`
  - Fields:
    - `message` (string): Confirmation message
  - Notes: Additional keys may be present and are accepted
- If provider returns no content, the client returns `None`

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

client = Timeback()
result = client.oneroster.rostering.delete_agent("user-sourced-id", "agent-sourced-id")
if result is not None:
    print(result.message)
```
