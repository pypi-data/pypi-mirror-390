## OneRoster — Rostering - Get Agent For

### GET /ims/oneroster/rostering/v1p2/users/{userId}/agentFor

- Method: GET
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Get users this user is an agent for (e.g., parents getting children list)

Path params:

- `userId` (string, required): The sourcedId of the user

Successful response (HTTP 200):

- Body: `{ "users": [User, ...] }`
- The `users` array contains `User` objects that this user is an agent for
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
result = client.oneroster.rostering.get_agent_for("<userId>")

print(f"Found {len(result.users)} users")
for user in result.users:
    print(user.sourcedId, user.givenName, user.familyName)
```

Notes:

- This endpoint returns a simple array response (not paginated), unlike `get_all_users` which includes pagination metadata.
- The response will contain an empty `users` array if the user is not an agent for any other users.

