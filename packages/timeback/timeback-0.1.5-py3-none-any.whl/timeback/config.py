import os
from typing import Literal

from timeback.errors import ConfigurationError


AllowedEnvironment = Literal["production", "staging"]


class Settings:
    """Validated client configuration loaded from environment variables.

    Required env vars:
      - TIMEBACK_CLIENT_ID
      - TIMEBACK_CLIENT_SECRET
      - TIMEBACK_ENVIRONMENT (currently only 'production' is supported)
    Optional env vars (override per-service base URLs):
      - TIMEBACK_QTI_API_BASE_URL (defaults by environment)
      - TIMEBACK_CALIPER_API_BASE_URL (defaults by environment)
    """

    def __init__(self, client_id: str | None = None, client_secret: str | None = None, environment: str | None = None, qti_api_base_url: str | None = None, caliper_api_base_url: str | None = None):
        self.client_id = client_id or os.getenv("TIMEBACK_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("TIMEBACK_CLIENT_SECRET")
        self.environment = environment or os.getenv("TIMEBACK_ENVIRONMENT")

        missing = []
        if not self.client_id:
            missing.append("TIMEBACK_CLIENT_ID")
        if not self.client_secret:
            missing.append("TIMEBACK_CLIENT_SECRET")
        if not self.environment:
            missing.append("TIMEBACK_ENVIRONMENT")

        if missing:
            raise ConfigurationError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        allowed: tuple[str, ...] = ("production", "staging")
        if self.environment not in allowed:
            raise ConfigurationError(
                f"Invalid TIMEBACK_ENVIRONMENT='{self.environment}'. Allowed values: {allowed}"
            )

        # Map environment to API and IDP URLs
        if self.environment == "production":
            self.api_base_url = "https://api.alpha-1edtech.ai/"
            self.idp_base_url = "https://prod-beyond-timeback-api-2-idp.auth.us-east-1.amazoncognito.com"
            default_qti = "https://qti.alpha-1edtech.ai/api"
            default_caliper = "https://caliper.alpha-1edtech.ai"
        elif self.environment == "staging":
            # Reserved for future use. If selected now, still configure endpoints.
            self.api_base_url = "https://api.staging.alpha-1edtech.ai/"
            self.idp_base_url = "https://alpha-auth-development-idp.auth.us-west-2.amazoncognito.com"
            default_qti = "https://qti-staging.alpha-1edtech.ai/api"
            default_caliper = "https://caliper-staging.alpha-1edtech.ai"

        # Normalize trailing slashes
        if not self.api_base_url.endswith("/"):
            self.api_base_url += "/"
        if not self.idp_base_url.endswith("/"):
            self.idp_base_url += "/"

        # Per-service base URLs with environment defaults and env/arg overrides
        env_qti = os.getenv("TIMEBACK_QTI_API_BASE_URL")
        env_caliper = os.getenv("TIMEBACK_CALIPER_API_BASE_URL")
        self.qti_api_base_url = (qti_api_base_url or env_qti or default_qti).rstrip("/")
        self.caliper_api_base_url = (caliper_api_base_url or env_caliper or default_caliper).rstrip("/")


