import time
from typing import Any, Dict, Optional

import httpx

from timeback.errors import NotFoundError, RateLimitError, RequestError, ServerError, AuthError
from timeback.models.errors import (
    TimebackBadRequestResponse,
    TimebackUnauthorizedRequestResponse,
    TimebackForbiddenResponse,
    TimebackNotFoundResponse,
    TimebackUnprocessableEntityResponse,
    TimebackTooManyRequestsResponse,
    TimebackInternalServerErrorResponse,
)


class HttpClient:
    """Thin wrapper around httpx.Client with auth header injection and basic retries."""

    def __init__(self, base_url: str, token_provider):
        self._base_url = base_url.rstrip("/")
        self._token_provider = token_provider
        self._client = httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0))

    def _headers(self) -> Dict[str, str]:
        token = self._token_provider.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        attempt = 0
        max_attempts = 3
        while True:
            attempt += 1
            start = time.time()
            try:
                resp = self._client.get(url, headers=self._headers(), params=params)
                duration = (time.time() - start) * 1000
                request_id = resp.headers.get("x-request-id") or resp.headers.get(
                    "x-amzn-requestid"
                )
                if 200 <= resp.status_code < 300:
                    return resp.json()
                self._raise_for_status(resp, request_id, duration)
            except RateLimitError:
                if attempt < max_attempts:
                    time.sleep(0.5 * attempt)
                    continue
                raise

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        attempt = 0
        max_attempts = 3
        while True:
            attempt += 1
            start = time.time()
            try:
                resp = self._client.post(url, headers=self._headers(), json=json)
                duration = (time.time() - start) * 1000
                request_id = resp.headers.get("x-request-id") or resp.headers.get(
                    "x-amzn-requestid"
                )
                if 200 <= resp.status_code < 300:
                    return resp.json()
                self._raise_for_status(resp, request_id, duration)
            except RateLimitError:
                if attempt < max_attempts:
                    time.sleep(0.5 * attempt)
                    continue
                raise

    def delete(self, path: str) -> Optional[Dict[str, Any]]:
        url = f"{self._base_url}{path}"
        attempt = 0
        max_attempts = 3
        while True:
            attempt += 1
            start = time.time()
            try:
                resp = self._client.delete(url, headers=self._headers())
                duration = (time.time() - start) * 1000
                request_id = resp.headers.get("x-request-id") or resp.headers.get(
                    "x-amzn-requestid"
                )
                if 200 <= resp.status_code < 300:
                    if not resp.text:
                        return None
                    return resp.json()
                self._raise_for_status(resp, request_id, duration)
            except RateLimitError:
                if attempt < max_attempts:
                    time.sleep(0.5 * attempt)
                    continue
                raise

    def put(self, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}{path}"
        attempt = 0
        max_attempts = 3
        while True:
            attempt += 1
            start = time.time()
            try:
                resp = self._client.put(url, headers=self._headers(), json=json)
                duration = (time.time() - start) * 1000
                request_id = resp.headers.get("x-request-id") or resp.headers.get(
                    "x-amzn-requestid"
                )
                if 200 <= resp.status_code < 300:
                    return resp.json()
                self._raise_for_status(resp, request_id, duration)
            except RateLimitError:
                if attempt < max_attempts:
                    time.sleep(0.5 * attempt)
                    continue
                raise

    @staticmethod
    def _raise_for_status(
        resp: httpx.Response, request_id: Optional[str], duration_ms: float
    ) -> None:
        status = resp.status_code
        msg_ctx = f"status={status} path={resp.request.url.path} duration_ms={duration_ms:.1f}"
        if request_id:
            msg_ctx += f" request_id={request_id}"
        body_excerpt = resp.text[:500]
        parsed = None
        try:
            data = resp.json()
        except Exception:
            data = None

        # Try to parse into OneRoster error models where applicable
        try:
            if status == 400 and isinstance(data, dict):
                parsed = TimebackBadRequestResponse.model_validate(data)
            elif status == 401 and isinstance(data, dict):
                parsed = TimebackUnauthorizedRequestResponse.model_validate(data)
            elif status == 403 and isinstance(data, dict):
                parsed = TimebackForbiddenResponse.model_validate(data)
            elif status == 404 and isinstance(data, dict):
                parsed = TimebackNotFoundResponse.model_validate(data)
            elif status == 422 and isinstance(data, dict):
                parsed = TimebackUnprocessableEntityResponse.model_validate(data)
            elif status == 429 and isinstance(data, dict):
                parsed = TimebackTooManyRequestsResponse.model_validate(data)
            elif 500 <= status < 600 and isinstance(data, dict):
                parsed = TimebackInternalServerErrorResponse.model_validate(data)
        except Exception:
            parsed = None

        if status == 404:
            raise NotFoundError(
                f"Resource not found ({msg_ctx}). Body: {body_excerpt}",
                error_details=parsed,
            )
        if status == 429:
            raise RateLimitError(
                f"Rate limited ({msg_ctx}). Body: {body_excerpt}",
                error_details=parsed,
            )
        if status == 401:
            raise AuthError(
                f"Unauthorized ({msg_ctx}). Body: {body_excerpt}",
                error_details=parsed,
            )
        if 500 <= status < 600:
            raise ServerError(
                f"Server error ({msg_ctx}). Body: {body_excerpt}",
                error_details=parsed,
            )
        raise RequestError(
            f"Request failed ({msg_ctx}). Body: {body_excerpt}",
            error_details=parsed,
        )
