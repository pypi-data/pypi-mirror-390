## OneRoster — Rostering - Get Agents

### GET /ims/oneroster/rostering/v1p2/users/{userId}/agents

- Method: GET
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Get agent users for a specified user.

Path params:

- `userId` (string, required): The sourcedId of the user

Successful response (HTTP 200):

- Body: `{ "agents": [User, ...] }`
- The `agents` array contains full `User` objects who are agents of the specified user
- Each `User` object includes (non-exhaustive):
  - required: `sourcedId`, `status`, `enabledUser`, `givenName`, `familyName`, `roles`, `agents`, `userProfiles`
  - optional: `username`, `userIds`, `middleName`, `primaryOrg`, `email`, `grades`, `dateLastModified`, `metadata`, etc.

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
result = client.oneroster.rostering.get_agents("<userId>")

print(f"Found {len(result.agents)} agents")
for user in result.agents:
    print(user.sourcedId, user.givenName, user.familyName)
```

Notes:

- This endpoint returns a simple array response (not paginated), unlike `get_all_users` which includes pagination metadata.


