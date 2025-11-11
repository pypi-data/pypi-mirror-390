"""Simple API key authentication helpers for the Saf3AI SDK."""

from __future__ import annotations

import threading
from typing import Dict, Optional

from saf3ai_sdk.logging import logger


class AuthenticationError(Exception):
    """Raised when SDK authentication fails."""


class AuthManager:
    """Singleton manager responsible for validating API keys."""

    _instance: Optional["AuthManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "AuthManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.enabled: bool = False
        self._default_api_key: Optional[str] = None
        self._header_name: str = "X-API-Key"
        self._initialized = True

    def configure(
        self,
        *,
        enabled: bool,
        api_key: Optional[str],
        header_name: Optional[str] = "X-API-Key",
    ) -> None:
        """
        Configure authentication settings.

        Args:
            enabled: Whether authentication is enforced.
            api_key: Default API key to attach to outbound requests.
            header_name: HTTP header name used for the API key.
        """

        self.enabled = enabled
        self._header_name = header_name or "X-API-Key"
        self._default_api_key = api_key

        if enabled:
            if api_key:
                logger.debug("SDK authentication enabled with provided API key.")
            else:
                logger.debug(
                    "SDK authentication enabled. Expect API key to be supplied per call."
                )
        else:
            logger.debug("SDK authentication disabled.")

    def verify(self, api_key: Optional[str] = None) -> str:
        """
        Validate the provided API key (or fallback to the configured default).
        """

        key = api_key or self._default_api_key

        if self.enabled and not key:
            raise AuthenticationError("Missing API key for authenticated request.")

        return key or ""

    def build_headers(self, api_key: Optional[str] = None) -> Dict[str, str]:
        """
        Construct authentication headers for outbound requests.
        """

        headers: Dict[str, str] = {}
        key = self.verify(api_key)

        if key and self._header_name:
            headers[self._header_name] = key

        return headers


auth_manager = AuthManager()

__all__ = ["auth_manager", "AuthManager", "AuthenticationError"]

