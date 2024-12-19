"""Binary sensors for Dolby CP750."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import DolbyCP750Coordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Dolby CP750 binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    name = hass.data[DOMAIN][config_entry.entry_id]["name"]
    unique_id = config_entry.unique_id or config_entry.entry_id

    # Create sensors for digital inputs 1-4
    entities = [
        DolbyCP750DigitalInput(
            coordinator,
            name,
            unique_id,
            i
        ) for i in range(1, 5)
    ]
    
    async_add_entities(entities)

class DolbyCP750DigitalInput(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for digital input validity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DolbyCP750Coordinator,
        name: str,
        unique_id: str,
        input_number: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._input_number = input_number
        self._attr_name = f"Digital {input_number} Valid"
        self._attr_unique_id = f"{unique_id}_dig_{input_number}_valid"
        self._attr_device_class = BinarySensorDeviceClass.SIGNAL

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=name,
            manufacturer="Dolby",
            model="CP750",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the digital input is valid."""
        if self.coordinator.data:
            return self.coordinator.data.get(f"dig_{self._input_number}_valid")
        return None