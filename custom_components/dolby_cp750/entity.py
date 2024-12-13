"""Custom entity platform for Dolby CP750."""
from __future__ import annotations

import logging
from typing import Any, Final, Optional

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    DolbyCP750Protocol,
    INPUT_SOURCES,
    SERVICE_SET_INPUT,
    SERVICE_SET_FADER,
    SERVICE_SET_MUTE,
    ATTR_FADER,
    ATTR_INPUT,
    ATTR_MUTE,
    ATTR_POWER,
    ATTR_CONNECTED,
)

_LOGGER = logging.getLogger(__name__)

# Schema validazione invariato...
SET_FADER_SCHEMA = {
    vol.Required("value"): vol.All(
        vol.Coerce(float), 
        vol.Range(min=-90.0, max=10.0)
    )
}

SET_INPUT_SCHEMA = {
    vol.Required("source"): vol.In(list(INPUT_SOURCES.values()))
}

SET_MUTE_SCHEMA = {
    vol.Required("mute"): cv.boolean
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 from a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    protocol = DolbyCP750Protocol(config["host"], config["port"])
    
    entity = DolbyCP750Entity(
        config["name"],
        protocol,
        config.get("power_switch"),  # Now optional
        config_entry.unique_id or config["host"]
    )
    
    async_add_entities([entity])

    # Registrazione servizi invariata...
    platform = entity_platform.async_get_current_platform()
    
    platform.async_register_entity_service(
        SERVICE_SET_FADER,
        SET_FADER_SCHEMA,
        "async_set_fader",
    )
    
    platform.async_register_entity_service(
        SERVICE_SET_INPUT,
        SET_INPUT_SCHEMA,
        "async_set_input",
    )
    
    platform.async_register_entity_service(
        SERVICE_SET_MUTE,
        SET_MUTE_SCHEMA,
        "async_set_mute",
    )

class DolbyCP750Entity(Entity):
    """Representation of a Dolby CP750 processor."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(
        self,
        name: str,
        protocol: DolbyCP750Protocol,
        power_switch: Optional[str],
        unique_id: str,
    ) -> None:
        """Initialize the entity."""
        self._attr_name = name
        self._protocol = protocol
        self._power_switch = power_switch
        self._attr_unique_id = unique_id
        
        self._fader = -90.0
        self._input = "dig_1"
        self._mute = False
        self._connected = False
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{protocol.host}",
        )

    async def _check_power_switch(self) -> bool:
        """Check if power switch is on (if configured)."""
        if not self._power_switch:
            return True  # No switch configured, assume powered
        
        power_state = await self.hass.states.async_get(self._power_switch)
        if not power_state:
            _LOGGER.warning("Configured power switch %s not found", self._power_switch)
            return True  # Switch not found, assume powered
        
        return power_state.state == STATE_ON

    @property
    def state(self) -> str:
        """Return the state of the device."""
        return STATE_ON if self._connected else STATE_OFF

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return "mdi:speaker" if self._connected else "mdi:speaker-off"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes = {
            ATTR_FADER: self._fader,
            ATTR_INPUT: INPUT_SOURCES.get(self._input, self._input),
            ATTR_MUTE: self._mute,
            ATTR_CONNECTED: self._connected,
        }
        
        if self._power_switch:
            attributes[ATTR_POWER] = self._power_switch
            
        return attributes

    async def async_update(self) -> None:
        """Update the entity."""
        try:
            # Check power switch only if configured
            if not await self._check_power_switch():
                self._connected = False
                return

            # Get fader level
            response = await self._protocol.send_command("cp750.sys.fader ?")
            self._fader = float(response.split()[1])

            # Get input source
            response = await self._protocol.send_command("cp750.sys.input_mode ?")
            self._input = response.split()[1]

            # Get mute state
            response = await self._protocol.send_command("cp750.sys.mute ?")
            self._mute = response.split()[1] == "1"

            self._connected = True

        except Exception as err:
            _LOGGER.error("Failed to update CP750: %s", err)
            self._connected = False

    # I metodi per i servizi rimangono invariati ma controlliamo solo connected
    async def async_set_input(self, source: str) -> None:
        """Set input source."""
        if not self._connected:
            _LOGGER.warning("Device not connected, cannot set input")
            return

        for key, value in INPUT_SOURCES.items():
            if value == source:
                try:
                    await self._protocol.send_command(f"cp750.sys.input_mode {key}")
                    await self.async_update()
                except Exception as err:
                    _LOGGER.error("Failed to set input: %s", err)
                break

    async def async_set_fader(self, value: float) -> None:
        """Set fader level."""
        if not self._connected:
            _LOGGER.warning("Device not connected, cannot set fader")
            return

        try:
            await self._protocol.send_command(f"cp750.sys.fader {value}")
            await self.async_update()
        except Exception as err:
            _LOGGER.error("Failed to set fader: %s", err)

    async def async_set_mute(self, mute: bool) -> None:
        """Set mute state."""
        if not self._connected:
            _LOGGER.warning("Device not connected, cannot set mute")
            return

        try:
            await self._protocol.send_command(f"cp750.sys.mute {1 if mute else 0}")
            await self.async_update()
        except Exception as err:
            _LOGGER.error("Failed to set mute: %s", err)