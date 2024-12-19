"""Fader control for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 fader control."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    name = hass.data[DOMAIN][config_entry.entry_id]["name"]
    unique_id = config_entry.unique_id or config_entry.entry_id
    
    entity = DolbyCP750Fader(
        coordinator,
        name,
        unique_id
    )
    
    async_add_entities([entity])

class DolbyCP750Fader(CoordinatorEntity, NumberEntity):
    """Fader control for Dolby CP750."""

    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, 
        coordinator,
        name: str, 
        unique_id: str
    ) -> None:
        """Initialize the fader control."""
        super().__init__(coordinator)
        self._attr_name = f"{name} Fader"
        self._attr_unique_id = f"{unique_id}_fader"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{coordinator.protocol.host}",
        )

    @property
    def native_value(self) -> float | None:
        """Return the current fader value."""
        if self.coordinator.data:
            return self.coordinator.data.get("fader")
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the fader level."""
        try:
            # Assicuriamoci che il valore sia un intero nel range corretto
            int_value = round(max(0, min(100, value)))
            await self.coordinator.protocol.send_command(f"cp750.sys.fader {int_value}")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set fader: %s", err)