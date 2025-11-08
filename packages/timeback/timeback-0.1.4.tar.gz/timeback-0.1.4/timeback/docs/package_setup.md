## Timeback Python Package Setup

This document explains how the client initializes configuration, authentication, and HTTP wiring, and how separate base URLs for OneRoster, QTI, and Caliper are handled.

### Overview

- **Top-level client**: `Timeback` in `timeback/client.py`
- **Configuration**: `Settings` in `timeback/config.py`
- **Auth**: OAuth2 Client Credentials via `OAuth2ClientCredentials` in `timeback/auth.py`
- **HTTP**: `HttpClient` in `timeback/http/http.py`
- **Services**: `OneRosterService` in `timeback/services/oneroster/oneroster.py` with `RosteringService` and the `get_user` endpoint available today

The client constructs separate `HttpClient` instances for each service family that may use different base URLs:
- OneRoster (uses the primary API base URL)
- QTI (dedicated base URL)
- Caliper (dedicated base URL)

### Environments and Base URLs

Environment is selected via `TIMEBACK_ENVIRONMENT` or passed to `Timeback(...)` as `environment`. Allowed values: `production`, `staging`.

Defaults per environment:
- **production**
  - OneRoster API base: `https://api.alpha-1edtech.ai/`
  - QTI API base: `https://qti.alpha-1edtech.ai/api`
  - Caliper API base: `https://caliper.alpha-1edtech.ai`
- **staging**
  - OneRoster API base: `https://api.staging.alpha-1edtech.ai/`
  - QTI API base: `https://qti-staging.alpha-1edtech.ai/api`
  - Caliper API base: `https://caliper-staging.alpha-1edtech.ai`

These defaults are defined in `timeback/config.py` and normalized (no trailing slash for QTI/Caliper; OneRoster retains trailing slash). You may override them via constructor args or environment variables (see below).

### Settings Configuration

File: `timeback/config.py`

Required environment variables:
- `TIMEBACK_CLIENT_ID`
- `TIMEBACK_CLIENT_SECRET`
- `TIMEBACK_ENVIRONMENT` (one of `production`, `staging`)

Optional per-service overrides:
- `TIMEBACK_QTI_API_BASE_URL`
- `TIMEBACK_CALIPER_API_BASE_URL`

Constructor overrides (take precedence over env):
- `Timeback(qti_api_base_url=..., caliper_api_base_url=...)`

### Authentication

File: `timeback/auth.py`

- Auth uses OAuth2 Client Credentials against the environment-specific IDP base URL defined in `Settings`.
- Tokens are cached in-memory and refreshed automatically before expiry.

IDP base URLs (current):
- production: `https://prod-beyond-timeback-api-2-idp.auth.us-east-1.amazoncognito.com`
- staging: `https://alpha-auth-development-idp.auth.us-west-2.amazoncognito.com`

Note: If QTI/Caliper require distinct IDPs later, the design allows introducing separate token providers without changing the external `Timeback` API.

### HTTP Client Wiring

File: `timeback/client.py`

On initialization, the client creates one token provider and three HTTP clients:
- `self._http_oneroster = HttpClient(base_url=self.settings.api_base_url, ...)`
- `self._http_qti = HttpClient(base_url=self.settings.qti_api_base_url, ...)`
- `self._http_caliper = HttpClient(base_url=self.settings.caliper_api_base_url, ...)`

Exposed properties:
- `self.oneroster` → `OneRosterService(self._http_oneroster)`
- `self.qti_http` → raw `HttpClient` for QTI base URL
- `self.caliper_http` → raw `HttpClient` for Caliper base URL

`HttpClient` performs bearer auth header injection and basic retry handling for GET requests, and raises typed errors for common failure cases.

### OneRoster Service Exposure

File: `timeback/services/oneroster/oneroster.py`

The OneRoster container currently exposes:
- `self.rostering` → `RosteringService`

Available endpoint today (example):
- `client.oneroster.rostering.get_user(sourced_id)`

### QTI and Caliper Access Points

We intentionally do not scaffold QTI/Caliper services yet. For now, the client exposes the configured HTTP clients:
- `client.qti_http` (use for calls to the QTI API base)
- `client.caliper_http` (use for calls to the Caliper API base)

This lets you start integrating quickly while keeping the codebase modular for future service classes.

### Usage Examples

Basic initialization using environment variables only:

```python
from timeback import Timeback

client = Timeback()
user = client.oneroster.rostering.get_user("sourced-id")
```

Override QTI and Caliper base URLs explicitly via constructor:

```python
from timeback import Timeback

client = Timeback(
    environment="staging",
    qti_api_base_url="https://my-qti.example.com/api",
    caliper_api_base_url="https://my-caliper.example.com",
)

# Existing OneRoster endpoint
user = client.oneroster.rostering.get_user("sourced-id")

# Raw HTTP clients for QTI / Caliper (service classes can be added later)
qti_health = client.qti_http.get("/health")
caliper_status = client.caliper_http.get("/status")
```

Override via environment variables:

```bash
export TIMEBACK_ENVIRONMENT=production
export TIMEBACK_CLIENT_ID=...        # required
export TIMEBACK_CLIENT_SECRET=...    # required

export TIMEBACK_QTI_API_BASE_URL=https://qti.custom.example.com/api
export TIMEBACK_CALIPER_API_BASE_URL=https://caliper.custom.example.com
```

### Future Extensions

- Introduce separate token providers if QTI/Caliper require distinct IDPs.
- Add dedicated service classes and endpoint modules for QTI and Caliper.
- Extend `HttpClient` with additional HTTP verbs as new write endpoints are added.


