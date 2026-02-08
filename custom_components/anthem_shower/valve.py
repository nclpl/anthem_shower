"""Valve platform for Anthem Shower."""

from __future__ import annotations

import logging

from homeassistant.components.valve import ValveEntity, ValveEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN
from .coordinator import AnthemCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Anthem Shower valve."""
    coordinator: AnthemCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnthemShowerValve(coordinator, entry)])


class AnthemShowerValve(CoordinatorEntity[AnthemCoordinator], ValveEntity):
    """Valve entity to start/stop the shower."""

    _attr_has_entity_name = True
    _attr_name = "Shower"
    _attr_icon = "mdi:shower-head"
    _attr_supported_features = ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
    _attr_reports_position = False

    def __init__(self, coordinator: AnthemCoordinator, entry: ConfigEntry) -> None:
        """Initialise the valve entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_shower_valve"
        host = entry.data[CONF_HOST]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Anthem Shower Hub",
            manufacturer="Anthem",
            model="Shower Hub",
            configuration_url=f"http://{host}",
        )

    @property
    def is_closed(self) -> bool:
        """Return True if the shower is not running."""
        if self.coordinator.data is None:
            return True
        return not self.coordinator.data.get("running", False)

    async def async_open_valve(self, **kwargs) -> None:
        """Turn on the shower."""
        temperature = self.coordinator.target_temperature
        _LOGGER.debug("Starting shower at %s F", temperature)
        await self.coordinator.client.start_water_test(temperature)
        await self.coordinator.async_request_refresh()

    async def async_close_valve(self, **kwargs) -> None:
        """Turn off the shower."""
        _LOGGER.debug("Stopping shower")
        await self.coordinator.client.stop_water_test()
        await self.coordinator.async_request_refresh()
