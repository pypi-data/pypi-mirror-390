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
from timeback.models.request import TimebackGetAllUsersRequest, TimebackQueryParams

client = Timeback()

# Basic request without query params
request = TimebackGetAllUsersRequest()
response = client.oneroster.rostering.get_all_users(request)

# With query params
query_params = TimebackQueryParams(
    limit=50,
    filter="status='active'",
    search="john"
)
request_with_params = TimebackGetAllUsersRequest(query_params=query_params)
response_filtered = client.oneroster.rostering.get_all_users(request_with_params)

print(response_filtered.totalCount, len(response_filtered.users))
if response_filtered.users:
    print(response_filtered.users[0].sourcedId, response_filtered.users[0].givenName, response_filtered.users[0].familyName)
```

Notes:

- The `order_by` field in `TimebackQueryParams` maps to `orderBy` in the API query.
- The `fields` field accepts a string or list of strings; lists are joined with commas.

