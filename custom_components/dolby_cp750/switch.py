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

from .const import (
    DOMAIN,
    DolbyCP750Protocol,
)
from .coordinator import DolbyCP750Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 switches."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    protocol = DolbyCP750Protocol(
        hass,
        config["host"], 
        config["port"],
        config.get("power_switch")
    )
    
    coordinator = DolbyCP750Coordinator(
        hass,
        protocol,
        config["name"]
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    entities = [
        DolbyCP750Mute(
            coordinator,
            config["name"],
            protocol,
            config_entry.unique_id or config["host"]
        )
    ]

    # Add power switch if configured
    if power_switch := config.get("power_switch"):
        entities.append(
            DolbyCP750Power(
                coordinator,
                config["name"],
                protocol,
                config_entry.unique_id or config["host"],
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
        coordinator: DolbyCP750Coordinator,
        name: str, 
        protocol: DolbyCP750Protocol, 
        unique_id: str,
    ) -> None:
        """Initialize the mute switch."""
        super().__init__(coordinator)
        self._attr_name = f"{name} Mute"
        self._protocol = protocol
        self._attr_unique_id = f"{unique_id}_mute"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{protocol.host}",
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if mute is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("mute")
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on mute."""
        try:
            await self._protocol.send_command("cp750.sys.mute 1")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on mute: %s", err)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off mute."""
        try:
            await self._protocol.send_command("cp750.sys.mute 0")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off mute: %s", err)

class DolbyCP750Power(CoordinatorEntity, SwitchEntity):
    """Power switch for Dolby CP750."""

    _attr_has_entity_name = True

    def __init__(
        self, 
        coordinator: DolbyCP750Coordinator,
        name: str, 
        protocol: DolbyCP750Protocol, 
        unique_id: str,
        power_switch: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the power switch."""
        super().__init__(coordinator)
        self._attr_name = f"{name} Power"
        self._protocol = protocol
        self._attr_unique_id = f"{unique_id}_power"
        self._power_switch = power_switch
        self._hass = hass
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
            configuration_url=f"http://{protocol.host}",
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
        state = self._hass.states.get(self._power_switch)
        return state.state == STATE_ON

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the device."""
        await self._hass.services.async_call(
            "switch", 
            "turn_on", 
            {"entity_id": self._power_switch},
            blocking=True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the device."""
        await self._hass.services.async_call(
            "switch", 
            "turn_off", 
            {"entity_id": self._power_switch},
            blocking=True
        )
        await self.coordinator.async_request_refresh()