## OneRoster — Rostering - Update User

### PUT /ims/oneroster/rostering/v1p2/users/{sourcedId}

- Method: PUT
- Auth: OAuth2 Client Credentials (Bearer token)
- Description: Update an existing user identified by `sourcedId`.

Path params:

- `sourcedId` (string, required): The user to update

Request body (application/json):

- `{ "user": { ... } }` with required fields:
  - `enabledUser` (boolean)
  - `givenName` (string)
  - `familyName` (string)
  - `roles` (array of role assignments)
  - `email` (string, email)

Optional fields include: `status`, `metadata`, `userMasterIdentifier`, `username`, `userIds`, `middleName`, `primaryOrg`, `preferredFirstName`, `preferredMiddleName`, `preferredLastName`, `pronouns`, `grades`, `password`, `sms`, `phone`, `agents`.

Successful response (HTTP 200):

- Body: `{ "user": TimebackUser }`

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
from timeback.models.request import TimebackUpdateUserRequest, TimebackUpdateUserBody
from timeback.models.timeback_user_role import TimebackUserRole
from timeback.enums.timeback_role_type import TimebackRoleType
from timeback.enums.timeback_role_name import TimebackRoleName
from timeback.models.timeback_org_ref import TimebackOrgRef

client = Timeback()
body = TimebackUpdateUserBody(
    enabledUser=True,
    givenName="Alice",
    familyName="Baker",
    email="alice@example.com",
    roles=[TimebackUserRole(roleType=TimebackRoleType.PRIMARY, role=TimebackRoleName.TEACHER, org=TimebackOrgRef(sourcedId="org1"))],
)
req = TimebackUpdateUserRequest(user=body)
user = client.oneroster.rostering.update_user("u1", req)
```

Notes:

- `enabledUser` accepts string values "true"/"false" and normalizes to boolean in the request model.

