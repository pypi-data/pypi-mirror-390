import threading
import time
from typing import Optional

import httpx

from timeback.errors import AuthError


class OAuth2ClientCredentials:
    """Simple OAuth2 Client Credentials token provider with in-memory cache."""

    def __init__(self, idp_base_url: str, client_id: str, client_secret: str):
        self._token: Optional[str] = None
        self._expiry_ts: float = 0
        self._lock = threading.Lock()
        self._idp_token_url = f"{idp_base_url.rstrip('/')}/oauth2/token"
        self._client_id = client_id
        self._client_secret = client_secret

    def get_access_token(self) -> str:
        now = time.time()
        # Refresh if missing or expiring within 60 seconds
        if not self._token or now >= self._expiry_ts - 60:
            with self._lock:
                # Double-check inside the lock
                if not self._token or time.time() >= self._expiry_ts - 60:
                    self._refresh_token()
        return self._token  # type: ignore[return-value]

    def _refresh_token(self) -> None:
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    self._idp_token_url,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    },
                )
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            expires_in = int(data.get("expires_in", 0))
            if not token:
                raise AuthError("IDP did not return access_token")
            self._token = token
            self._expiry_ts = time.time() + max(expires_in, 0)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            body = e.response.text[:500]
            raise AuthError(
                f"Auth failed (status {status}). Check client id/secret. Response: {body}"
            ) from e
        except Exception as e:
            raise AuthError(f"Auth failed: {e}") from e


