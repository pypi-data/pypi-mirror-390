## OneRoster — Rostering - Add Agent

### POST /ims/oneroster/rostering/v1p2/users/{userId}/agents

- Method: POST
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Add an agent for a user.

Request model:

- `TimebackAddAgentRequest` with required fields:
  - `user_id` (string) — The sourcedId of the user (used in path)
  - `agent_sourced_id` (string) — The sourcedId of the agent to add (used in request body)

Path params (extracted from request):

- `userId` (string, required): The sourcedId of the user

Request body (application/json, extracted from request):

- `{ "agentSourcedId": string }` with required fields:
  - `agentSourcedId` (string) — The sourcedId of the agent to add

Successful response (HTTP 200):

- Body: `{ "message": string, ... }` (additional properties allowed)
- Key fields:
  - `message` (string, optional) — Confirmation message from the provider

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
from timeback.models.request import TimebackAddAgentRequest

client = Timeback()
user_id = "31129aea-12b2-4e9e-a6e5-f5c8b712d674"
agent_sourced_id = "agent-123-456-789"
request = TimebackAddAgentRequest(user_id=user_id, agent_sourced_id=agent_sourced_id)
resp = client.oneroster.rostering.add_agent(request)
print(resp.get("message", "Agent added successfully"))
```

Notes:

- The response is a dictionary that may include a `message` field and other provider-specific fields.

