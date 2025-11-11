from timeback.config import Settings
from timeback.auth import OAuth2ClientCredentials
from timeback.http import HttpClient
from timeback.services.oneroster import OneRosterService


class Timeback:
    """Top-level client users import via `from timeback import Timeback`.

    Usage:
        client = Timeback()
        user = client.oneroster.rostering.get_user("sourced-id")
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        environment: str | None = None,
        qti_api_base_url: str | None = None,
        caliper_api_base_url: str | None = None,
    ):
        self.settings = Settings(
            client_id=client_id,
            client_secret=client_secret,
            environment=environment,
            qti_api_base_url=qti_api_base_url,
            caliper_api_base_url=caliper_api_base_url,
        )
        token_provider = OAuth2ClientCredentials(
            idp_base_url=self.settings.idp_base_url,
            client_id=self.settings.client_id,  # type: ignore[arg-type]
            client_secret=self.settings.client_secret,  # type: ignore[arg-type]
        )
        # Create distinct HTTP clients per service family. OneRoster shares the main API base URL;
        # QTI and Caliper have dedicated base URLs that may differ by environment.
        self._http_oneroster = HttpClient(
            base_url=self.settings.api_base_url, token_provider=token_provider
        )
        self._http_qti = HttpClient(
            base_url=self.settings.qti_api_base_url, token_provider=token_provider
        )
        self._http_caliper = HttpClient(
            base_url=self.settings.caliper_api_base_url, token_provider=token_provider
        )

        # Expose existing services
        self.oneroster = OneRosterService(self._http_oneroster)

        # Expose raw HTTP clients for future QTI/Caliper services without scaffolding now
        self.qti_http = self._http_qti
        self.caliper_http = self._http_caliper
