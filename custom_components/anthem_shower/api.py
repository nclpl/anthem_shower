"""API client for Anthem Shower hub."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import time
import uuid

import aiohttp

from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from .const import ANTHEM_RSA_PUBLIC_KEY_PEM

_LOGGER = logging.getLogger(__name__)

TOKEN_EXPIRY_BUFFER = 60  # seconds


class AnthemAuthError(Exception):
    """Authentication failed."""


class AnthemConnectionError(Exception):
    """Connection to hub failed."""


class AnthemApiClient:
    """Client for the Anthem shower local API."""

    def __init__(self, host: str, pin: str, session: aiohttp.ClientSession) -> None:
        """Initialise the client."""
        self._host = host
        self._pin = pin
        self._session = session
        self._token: str | None = None
        self._token_exp: float = 0
        self._public_key = load_pem_public_key(ANTHEM_RSA_PUBLIC_KEY_PEM.encode())

    @property
    def _base_url(self) -> str:
        return f"http://{self._host}/web/api/v1/device"

    def _common_headers(self, token: str | None = None) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "random_uuid": str(uuid.uuid4()),
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _encrypt_pin(self) -> str:
        """SHA-256 hash the PIN then RSA-encrypt it, returning base64."""
        pin_hash = hashlib.sha256(self._pin.encode()).hexdigest()
        encrypted = self._public_key.encrypt(
            pin_hash.encode(),
            asym_padding.PKCS1v15(),
        )
        return base64.b64encode(encrypted).decode()

    async def _authenticate(self) -> str:
        """Login and return a JWT token."""
        url = f"{self._base_url}/request_user_login"
        payload = {
            "req_command": "login",
            "pin": self._encrypt_pin(),
        }
        try:
            async with self._session.post(
                url, json=payload, headers=self._common_headers(), timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise AnthemConnectionError(f"Cannot connect to Anthem hub at {self._host}") from err

        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise AnthemAuthError(f"Login failed: {data}")

        # Parse JWT expiry
        try:
            jwt_payload = json.loads(
                base64.b64decode(token.split(".")[1] + "==")
            )
            self._token_exp = jwt_payload.get("exp", 0)
        except Exception:
            # Fallback: assume 10 min validity
            self._token_exp = time.time() + 600

        self._token = token
        _LOGGER.debug("Anthem token refreshed, expires %s", self._token_exp)
        return token

    async def _ensure_token(self) -> str:
        """Return a valid token, refreshing if needed."""
        now = time.time()
        if self._token and self._token_exp > (now + TOKEN_EXPIRY_BUFFER):
            return self._token
        return await self._authenticate()

    def invalidate_token(self) -> None:
        """Force re-auth on next request."""
        self._token = None
        self._token_exp = 0

    async def get_running_state(self) -> dict:
        """Poll the hub for its running state.

        Returns dict with keys:
          running: bool
          device_names: list[str]
        """
        token = await self._ensure_token()
        url = f"{self._base_url}/get_hub_running_state"

        try:
            async with self._session.get(
                url, headers=self._common_headers(token), timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 403:
                    self.invalidate_token()
                    raise AnthemAuthError("Token rejected (403)")
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise AnthemConnectionError(f"Status request failed: {err}") from err

        if not isinstance(data, dict):
            raise AnthemConnectionError(f"Unexpected response: {data}")

        if data.get("error") == "Unauthorised token":
            self.invalidate_token()
            raise AnthemAuthError("Token expired")

        if data.get("status") == "false":
            raise AnthemConnectionError(f"Hub returned error: {data}")

        return {
            "running": data.get("running") is True,
            "device_names": data.get("devicename", []),
        }

    async def async_test_connection(self) -> bool:
        """Test that we can auth and poll. Used by config flow."""
        await self.get_running_state()
        return True
