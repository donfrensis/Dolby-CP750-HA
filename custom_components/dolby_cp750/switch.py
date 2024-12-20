"""Mute and power switches for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import STATE_ON

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 switches."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    name = hass.data[DOMAIN][config_entry.entry_id]["name"]
    power_switch = hass.data[DOMAIN][config_entry.entry_id]["power_switch"]
    unique_id = config_entry.unique_id or config_entry.entry_id
    
    entities = [
        DolbyCP750Mute(
            coordinator,
            name,
            unique_id
        )
    ]

    if power_switch:
        entities.append(
            DolbyCP750Power(
                coordinator,
                name,
                unique_id,
                power_switch,
                hass
            )
        )
    
    async_add_entities(entities)

class DolbyCP750Mute(CoordinatorEntity, SwitchEntity):
    """Mute switch for Dolby CP750."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator,
        name: str, 
        unique_id: str,
    ) -> None:
        """Initialize the mute switch."""
        super().__init__(coordinator)
        self._attr_name = "Mute"
        self._attr_unique_id = f"{unique_id}_mute"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.protocol.available

    @property
    def is_on(self) -> bool | None:
        """Return True if mute is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("mute")
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on mute."""
        try:
            await self.coordinator.protocol.send_command("cp750.sys.mute 1")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on mute: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off mute."""
        try:
            await self.coordinator.protocol.send_command("cp750.sys.mute 0")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off mute: %s", err)

class DolbyCP750Power(CoordinatorEntity, SwitchEntity):
    """Power switch for Dolby CP750."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator,
        name: str, 
        unique_id: str,
        power_switch: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the power switch."""
        super().__init__(coordinator)
        self._attr_name = "Power"
        self._attr_unique_id = f"{unique_id}_power"
        self._power_switch = power_switch
        self._hass = hass
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
        )

    @property
    def available(self) -> bool:
        """Return if power switch is available."""
        state = self._hass.states.get(self._power_switch)
        return state is not None

    @property
    def is_on(self) -> bool | None:
        """Return True if device is on."""
        if not self.available:
            return None
        state = self