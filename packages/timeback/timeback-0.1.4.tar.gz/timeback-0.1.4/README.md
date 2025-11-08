# Timeback

Python client for the Timeback API (OneRoster 1.2 plus adjacent services).

## Installation

### Using Poetry (recommended)

```bash
poetry install
poetry shell
```

### From built wheel

```bash
poetry build
pip install dist/timeback-0.1.0-py3-none-any.whl
```

## Configuration

Required environment variables:

- `TIMEBACK_CLIENT_ID`
- `TIMEBACK_CLIENT_SECRET`
- `TIMEBACK_ENVIRONMENT` in {`production`, `staging`}

Optional per-service base URL overrides:

- `TIMEBACK_QTI_API_BASE_URL` (defaults by environment)
- `TIMEBACK_CALIPER_API_BASE_URL` (defaults by environment)

Defaults by environment:

- production
  - OneRoster: `https://api.alpha-1edtech.ai/`
  - QTI: `https://qti.alpha-1edtech.ai/api`
  - Caliper: `https://caliper.alpha-1edtech.ai`
- staging
  - OneRoster: `https://api.staging.alpha-1edtech.ai/`
  - QTI: `https://qti-staging.alpha-1edtech.ai/api`
  - Caliper: `https://caliper-staging.alpha-1edtech.ai`

## Quick start

```python
from timeback import Timeback

client = Timeback()
user = client.oneroster.rostering.get_user("<sourcedId>")
print(user.sourcedId, user.givenName, user.familyName)
```

Override QTI/Caliper base URLs explicitly:

```python
client = Timeback(
    environment="staging",
    qti_api_base_url="https://my-qti.example.com/api",
    caliper_api_base_url="https://my-caliper.example.com",
)

# Raw HTTP clients (services can be added later)
qti_health = client.qti_http.get("/health")
caliper_status = client.caliper_http.get("/status")
```

Design rules: service methods contain no business logic; each method calls a single endpoint function in `timeback/services/.../endpoints/`, which may import utilities from `.../utils/`. All endpoints/utilities return typed Pydantic models/enums from `timeback/models` and `timeback/enums`.

See docs for structure and procedures:

- `timeback/docs/oneroster/rostering/get_user.md`
- `timeback/docs/oneroster/rostering/get_all_users.md`
