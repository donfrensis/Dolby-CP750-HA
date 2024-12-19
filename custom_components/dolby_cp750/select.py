"""Input selector for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    INPUT_SOURCES,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 input selector."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    name = hass.data[DOMAIN][config_entry.entry_id]["name"]
    unique_id = config_entry.unique_id or config_entry.entry_id
    
    entity = DolbyCP750InputSelect(
        coordinator,
        name,
        unique_id
    )
    
    async_add_entities([entity])

class DolbyCP750InputSelect(CoordinatorEntity, SelectEntity):
    """Input selector for Dolby CP750."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator,
        name: str, 
        unique_id: str
    ) -> None:
        """Initialize the input selector."""
        super().__init__(coordinator)
        self._attr_name = f"{name} Input"
        self._attr_unique_id = f"{unique_id}_input"
        self._attr_options = list(INPUT_SOURCES.values())
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{coordinator.protocol.host}",
        )

    @property
    def current_option(self) -> str | None:
        """Return the current input source."""
        if self.coordinator.data:
            input_key = self.coordinator.data.get("input")
            if input_key:
                return INPUT_SOURCES.get(input_key)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change input source."""
        for key, value in INPUT_SOURCES.items():
            if value == option:
                try:
                    await self.coordinator.protocol.send_command(f"cp750.sys.input_mode {key}")
                    await self.coordinator.async_request_refresh()
                except Exception as err:
                    _LOGGER.error("Failed to set input: %s", err)
                break