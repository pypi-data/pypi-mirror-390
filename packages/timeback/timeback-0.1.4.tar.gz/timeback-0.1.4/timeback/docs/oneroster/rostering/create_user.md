## OneRoster — Rostering - Create User

### POST /ims/oneroster/rostering/v1p2/users/

- Method: POST
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Create a new user.

Path params:

- None

Request body (application/json):

- `{ "user": { ... } }` with required fields:
  - `sourcedId` (string) — optional; if omitted, this package auto-generates a UUID
  - `enabledUser` (boolean)
  - `givenName` (string)
  - `familyName` (string)
  - `roles` (array of role assignments)
  - `email` (string, email)

Successful response (HTTP 201):

- Body (per spec):
  - `{ "sourcedIdPairs": { "suppliedSourcedId": string, "allocatedSourcedId": string } }`

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
from timeback.models.request import TimebackCreateUserRequest, TimebackCreateUserBody
from timeback.models.timeback_user_role import TimebackUserRole
from timeback.enums.timeback_role_type import TimebackRoleType
from timeback.enums.timeback_role_name import TimebackRoleName
from timeback.models.timeback_org_ref import TimebackOrgRef

client = Timeback()
body = TimebackCreateUserBody(
    # sourcedId may be provided; if omitted, a UUID is generated automatically
    enabledUser=True,
    givenName="Chris",
    familyName="Doe",
    email="chris@example.com",
    roles=[TimebackUserRole(roleType=TimebackRoleType.PRIMARY, role=TimebackRoleName.STUDENT, org=TimebackOrgRef(sourcedId="org1"))],
)
req = TimebackCreateUserRequest(user=body)
resp = client.oneroster.rostering.create_user(req)
print(resp.sourcedIdPairs.suppliedSourcedId, '->', resp.sourcedIdPairs.allocatedSourcedId)
```

Notes:

- `sourcedId` is required and must be non-empty; Timeback returns `sourcedIdPairs` mapping your supplied ID to the allocated ID.
- `enabledUser` accepts string values "true"/"false" and normalizes to boolean in the request model.

