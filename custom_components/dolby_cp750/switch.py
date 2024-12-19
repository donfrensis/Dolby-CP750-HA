"""Mute switch for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up the Dolby CP750 mute switch."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    protocol = DolbyCP750Protocol(
        hass,
        config["host"], 
        config["port"],
        config.get("power_switch")
    )
    
    entity = DolbyCP750Mute(
        config["name"],
        protocol,
        config_entry.unique_id or config["host"]
    )
    
    async_add_entities([entity])

class DolbyCP750Mute(SwitchEntity):
    """Mute switch for Dolby CP750."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(self, name: str, protocol: DolbyCP750Protocol, unique_id: str) -> None:
        """Initialize the mute switch."""
        self._attr_name = f"{name} Mute"
        self._protocol = protocol
        self._attr_unique_id = f"{unique_id}_mute"
        self._is_on = False
        
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
    def is_on(self) -> bool:
        """Return True if mute is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on mute."""
        try:
            await self._protocol.send_command("cp750.sys.mute 1")
            self._is_on = True
        except Exception as err:
            _LOGGER.error("Failed to turn on mute: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off mute."""
        try:
            await self._protocol.send_command("cp750.sys.mute 0")
            self._is_on = False
        except Exception as err:
            _LOGGER.error("Failed to turn off mute: %s", err)

#    async def async_update(self) -> None:
#        """Update the current mute state."""
#        try:
#            response = await self._protocol.send_command("cp750.sys.mute ?")
#            self._is_on = response.split()[-1] == "1"
#        except Exception as err:
#            _LOGGER.error("Failed to update mute: %s", err)

    async def async_update(self) -> None:
        """Update the current mute state."""
        try:
            response = await self._protocol.send_command("cp750.sys.mute ?")
            _LOGGER.debug("Mute response: %s", response)
        
            # La risposta dovrebbe essere tipo "cp750.sys.mute 1"
            parts = response.split()
            if len(parts) >= 3 and parts[0] == "cp750.sys.mute":
                value = parts[-1]
                if value in ["0", "1"]:
                    self._is_on = value == "1"
                    _LOGGER.debug("Valid mute value: %s -> %s", value, self._is_on)
                else:
                    _LOGGER.warning("Invalid mute value: %s", value)
            else:
                _LOGGER.warning("Unexpected mute response format: %s", response)
        except Exception as err:
            _LOGGER.error("Failed to update mute: %s", err)