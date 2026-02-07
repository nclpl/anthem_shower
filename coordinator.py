"""DataUpdateCoordinator for Anthem Shower."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AnthemApiClient, AnthemAuthError, AnthemConnectionError

_LOGGER = logging.getLogger(__name__)


class AnthemCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Anthem hub."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AnthemApiClient,
        scan_interval: int,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Anthem Shower",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch running state from the hub."""
        try:
            return await self.client.get_running_state()
        except AnthemAuthError:
            # Token expired mid-cycle; retry once with fresh token
            try:
                return await self.client.get_running_state()
            except AnthemAuthError as err:
                # Two consecutive auth failures → PIN is likely invalid
                raise ConfigEntryAuthFailed(
                    "Authentication failed. The PIN may have been changed on the hub."
                ) from err
            except AnthemConnectionError as err:
                raise UpdateFailed(str(err)) from err
        except AnthemConnectionError as err:
            raise UpdateFailed(str(err)) from err
