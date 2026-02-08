"""Number platform for Anthem Shower."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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
    """Set up the Anthem Shower target temperature number."""
    coordinator: AnthemCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AnthemTargetTemperature(coordinator, entry)])


class AnthemTargetTemperature(CoordinatorEntity[AnthemCoordinator], NumberEntity):
    """Number entity for shower target temperature."""

    _attr_has_entity_name = True
    _attr_name = "Target Temperature"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 60.0
    _attr_native_max_value = 120.0
    _attr_native_step = 1.0
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: AnthemCoordinator, entry: ConfigEntry) -> None:
        """Initialise the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_target_temperature"
        self._attr_native_value = coordinator.target_temperature
        host = entry.data[CONF_HOST]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Anthem Shower Hub",
            manufacturer="Anthem",
            model="Shower Hub",
            configuration_url=f"http://{host}",
        )

    @property
    def native_value(self) -> float:
        """Return the current target temperature."""
        return self.coordinator.target_temperature

    async def async_set_native_value(self, value: float) -> None:
        """Set the target temperature."""
        self.coordinator.target_temperature = value
        self.async_write_ha_state()
