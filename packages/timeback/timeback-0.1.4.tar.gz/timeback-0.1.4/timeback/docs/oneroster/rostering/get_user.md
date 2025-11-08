## OneRoster — Rostering - Get User

### GET /ims/oneroster/rostering/v1p2/users/{sourcedId}

- Method: GET
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Fetch a specific OneRoster user by `sourcedId`.
- Query params:
- `fields` (string, optional): Comma-separated field list (e.g., `sourcedId,username`)

Path params:

- `sourcedId` (string, required): The user's sourcedId

Successful response (HTTP 200):

- Body: `{ "user": User }`
- The `User` object includes (non-exhaustive):
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
user = client.oneroster.rostering.get_user("<sourcedId>")
# With fields filter
user_min = client.oneroster.rostering.get_user("<sourcedId>", fields=["sourcedId", "username"])

print(user.sourcedId, user.givenName, user.familyName)
```

Notes:

- The client returns the raw API payload cast into the `TimebackUser` Pydantic model without transformation.
- If the API omits required fields, validation will fail with a `ParseError`.
