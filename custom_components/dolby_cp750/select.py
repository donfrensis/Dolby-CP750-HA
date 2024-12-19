"""Input selector for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    DolbyCP750Protocol,
    INPUT_SOURCES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 input selector."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    protocol = DolbyCP750Protocol(
        hass,
        config["host"], 
        config["port"],
        config.get("power_switch")
    )
    
    entity = DolbyCP750InputSelect(
        config["name"],
        protocol,
        config_entry.unique_id or config["host"]
    )
    
    async_add_entities([entity])

class DolbyCP750InputSelect(SelectEntity):
    """Input selector for Dolby CP750."""

    _attr_has_entity_name = True
    _attr_should_poll = True

    def __init__(self, name: str, protocol: DolbyCP750Protocol, unique_id: str) -> None:
        """Initialize the input selector."""
        self._attr_name = f"{name} Input"
        self._protocol = protocol
        self._attr_unique_id = f"{unique_id}_input"
        self._attr_options = list(INPUT_SOURCES.values())
        self._current = list(INPUT_SOURCES.values())[0]
        
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
    def current_option(self) -> str | None:
        """Return the current input source."""
        return self._current

    async def async_select_option(self, option: str) -> None:
        """Change input source."""
        for key, value in INPUT_SOURCES.items():
            if value == option:
                try:
                    await self._protocol.send_command(f"cp750.sys.input_mode {key}")
                    self._current = option
                except Exception as err:
                    _LOGGER.error("Failed to set input: %s", err)
                break

    async def async_update(self) -> None:
        """Update the current input."""
        try:
            response = await self._protocol.send_command("cp750.sys.input_mode ?")
            input_key = response.split()[-1]  # Prendiamo l'ultima parte
            self._current = INPUT_SOURCES.get(input_key, input_key)
        except Exception as err:
            _LOGGER.error("Failed to update input: %s", err)