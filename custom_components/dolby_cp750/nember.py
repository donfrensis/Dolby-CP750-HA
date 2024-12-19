"""Fader control for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    DolbyCP750Protocol,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 fader control."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    protocol = DolbyCP750Protocol(
        hass,
        config["host"], 
        config["port"],
        config.get("power_switch")
    )
    
    entity = DolbyCP750Fader(
        config["name"],
        protocol,
        config_entry.unique_id or config["host"]
    )
    
    async_add_entities([entity])

class DolbyCP750Fader(NumberEntity):
    """Fader control for Dolby CP750."""

    _attr_has_entity_name = True
    _attr_should_poll = True
    _attr_native_min_value = -90.0
    _attr_native_max_value = 10.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "dB"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, name: str, protocol: DolbyCP750Protocol, unique_id: str) -> None:
        """Initialize the fader control."""
        self._attr_name = f"{name} Fader"
        self._protocol = protocol
        self._attr_unique_id = f"{unique_id}_fader"
        self._value = -90.0
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{protocol.host}",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._protocol.available

    @property
    def native_value(self) -> float:
        """Return the current fader value."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the fader level."""
        try:
            await self._protocol.send_command(f"cp750.sys.fader {value}")
            self._value = value
        except Exception as err:
            _LOGGER.error("Failed to set fader: %s", err)

    async def async_update(self) -> None:
        """Update the current fader value."""
        try:
            response = await self._protocol.send_command("cp750.sys.fader ?")
            self._value = float(response.split()[1])
        except Exception as err:
            _LOGGER.error("Failed to update fader: %s", err)