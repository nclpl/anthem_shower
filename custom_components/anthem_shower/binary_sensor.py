"""Binary sensor platform for Anthem Shower."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN
from .coordinator import AnthemCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Anthem Shower binary sensor."""
    coordinator: AnthemCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnthemShowerBinarySensor(coordinator, entry)])


class AnthemShowerBinarySensor(CoordinatorEntity[AnthemCoordinator], BinarySensorEntity):
    """Binary sensor that reports whether the shower is running."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_has_entity_name = True
    _attr_name = "Shower"
    _attr_icon = "mdi:shower-head"

    def __init__(self, coordinator: AnthemCoordinator, entry: ConfigEntry) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        host = entry.data[CONF_HOST]
        self._attr_unique_id = f"{entry.entry_id}_shower_running"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Anthem Shower Hub",
            manufacturer="Anthem",
            model="Shower Hub",
            configuration_url=f"http://{host}",
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the shower is running."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("running", False)

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return active device names as an attribute."""
        if self.coordinator.data is None:
            return None
        names = self.coordinator.data.get("device_names", [])
        if names:
            return {"active_devices": names}
        return None
