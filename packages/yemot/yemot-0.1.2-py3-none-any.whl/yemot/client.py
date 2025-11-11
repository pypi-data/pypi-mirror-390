from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

import requests


class YemotError(RuntimeError):
    """Base exception for all Yemot API errors."""

    def __init__(self, message: str, payload: Optional[Mapping[str, Any]] = None):
        super().__init__(message)
        self.payload = payload or {}


class AuthenticationError(YemotError):
    """Raised when authentication with the Yemot API fails."""


class MFARequiredError(AuthenticationError):
    """Raised when the API demands multi-factor authentication for the session."""


def _clean_params(values: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Remove keys whose value is None."""

    cleaned: Dict[str, Any] = {}
    if not values:
        return cleaned
    for key, value in values.items():
        if value is None:
            continue
        cleaned[key] = value
    return cleaned


@dataclass
class Client:
    """Thin wrapper around the Yemot HTTP API."""

    username: str
    password: str
    base_url: str = "https://www.call2all.co.il/ym/api/"
    timeout: Union[int, float] = 30

    def __post_init__(self) -> None:
        if not self.base_url.endswith("/"):
            self.base_url = f"{self.base_url}/"
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        self._session = requests.Session()
        self.token: Optional[str] = None
        self.login()

    def close(self) -> None:
        """Close the underlying HTTP session."""

        self._session.close()

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> str:
        """Authenticate and obtain a fresh token."""

        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

        response = self._request(
            "GET",
            "Login",
            params={"username": self.username, "password": self.password},
            include_token=False,
            handle_api_errors=False,
        )

        token = response.get("token")
        status = response.get("responseStatus")
        if not token or status != "OK":
            message = response.get("message", "Username or password is incorrect")
            raise AuthenticationError(message, response)

        self.token = token
        return status

    def logout(self) -> Dict[str, Any]:
        """Invalidate the current token."""

        if not self.token:
            return {"message": "Already logged out"}
        response = self._request("GET", "Logout")
        self.token = None
        return response

    def get(self, web_service: str, params: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Perform a GET request against the Yemot API."""

        return self._request("GET", web_service, params=params)

    def post(
        self,
        web_service: str,
        data: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Perform a POST request against the Yemot API."""

        cleaned_data = _clean_params(data)
        return self._request("POST", web_service, data=cleaned_data, json=json)

    def post_file(
        self,
        web_service: str,
        *,
        file_path: Optional[str] = None,
        file_obj: Optional[Any] = None,
        data: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Upload a single file using multipart/form-data."""

        if not file_path and not file_obj:
            raise ValueError("Either file_path or file_obj must be provided")
        if file_path and file_obj:
            raise ValueError("Provide only one of file_path or file_obj")

        payload = _clean_params(data)
        files: Dict[str, Any]
        file_to_close = None

        if file_path:
            file_to_close = open(file_path, "rb")
            files = {"file": (Path(file_path).name, file_to_close)}
        else:
            files = {"file": file_obj}

        try:
            return self._request("POST", web_service, data=payload, files=files)
        finally:
            if file_to_close:
                file_to_close.close()

    def download(self, web_service: str, params: Optional[Mapping[str, Any]] = None) -> bytes:
        """Download binary data from the API (e.g. audio files)."""

        response = self._request(
            "GET",
            web_service,
            params=params,
            expect_json=False,
        )
        # _request returns raw requests.Response when expect_json=False
        return response.content

    def _request(
        self,
        method: str,
        web_service: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Mapping[str, Any]] = None,
        include_token: bool = True,
        expect_json: bool = True,
        retry: bool = True,
        handle_api_errors: bool = True,
    ) -> Union[Dict[str, Any], requests.Response]:
        if include_token and web_service.lower() != "login":
            if not self.token:
                self.login()
        query = _clean_params(params)
        body = data

        if include_token and web_service.lower() != "login":
            query = {"token": self.token, **query}

        url = f"{self.base_url}{web_service}"
        response = self._session.request(
            method,
            url,
            params=query or None,
            data=body,
            json=json,
            files=files,
            timeout=self.timeout,
        )
        if not expect_json:
            response.raise_for_status()
            return response

        try:
            payload = response.json()
        except ValueError as exc:
            response.raise_for_status()
            raise YemotError("Invalid JSON response", {"status_code": response.status_code}) from exc

        status = payload.get("responseStatus")
        message = payload.get("message")

        if handle_api_errors and status in {"ERROR", "FORBIDDEN"}:
            if message == "MFA_REQUIRED":
                raise MFARequiredError("Multi-factor authentication is required", payload)

            if retry and self._should_refresh_token(payload):
                self.login()
                return self._request(
                    method,
                    web_service,
                    params=params,
                    data=data,
                    json=json,
                    files=files,
                    include_token=include_token,
                    expect_json=expect_json,
                    retry=False,
                )

            raise YemotError(message or "Unknown API error", payload)

        return payload

    @staticmethod
    def _should_refresh_token(payload: Mapping[str, Any]) -> bool:
        message = str(payload.get("message", ""))
        if not message:
            return False
        normalized = message.upper()
        if normalized in {
            "TOKEN_NOT_FOUND",
            "TOKEN_EXPIRED",
            "INVALID_TOKEN",
            "LOGIN_REQUIRED",
        }:
            return True
        return "TOKEN" in normalized

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - trivial
        self.close()

