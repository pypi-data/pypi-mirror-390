## OneRoster — Rostering - Delete User

### DELETE /ims/oneroster/rostering/v1p2/users/{sourcedId}

- Method: DELETE
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Soft delete a user (sets status to `tobedeleted`).

Path params:

- `sourcedId` (string, required): The user to delete

Successful response (HTTP 204):

- No content

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
client.oneroster.rostering.delete_user("u1")
```


