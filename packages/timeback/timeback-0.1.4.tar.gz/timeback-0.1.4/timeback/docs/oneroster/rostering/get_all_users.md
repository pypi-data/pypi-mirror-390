## OneRoster — Rostering - Get All Users

### GET /ims/oneroster/rostering/v1p2/users

- Method: GET
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Get all Users on the service provider (paginated).

Query params:

- `fields` (string, optional): Comma-separated fields to include (e.g., `sourcedId,name`)
- `limit` (integer, optional, default 100, max 3000): Max items per page
- `offset` (integer, optional, default 0): Number of items to skip
- `sort` (string, optional): Field to sort by
- `orderBy` (string, optional, enum: `asc`, `desc`): Sort order
- `filter` (string, optional): OneRoster filter expression (e.g., `status='active'`)
- `search` (string, optional): Proprietary free-text search across multiple fields

Successful response (HTTP 200):

- Body: `{ "users": [User, ...], "totalCount": number, "pageCount": number, "pageNumber": number, "offset": number, "limit": number }`
- Key fields: `users`, `totalCount`, `pageCount`, `pageNumber`, `offset`, `limit`

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
resp = client.oneroster.rostering.get_all_users(limit=50, filter="status='active'", search="john")

print(resp.totalCount, len(resp.users))
if resp.users:
    print(resp.users[0].sourcedId, resp.users[0].givenName, resp.users[0].familyName)
```

Notes:

- `order_by` parameter in the Python client maps to `orderBy` in the API query.
- `fields` accepts a string or list of strings; lists are joined with commas.

