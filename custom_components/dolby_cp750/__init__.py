"""The Dolby CP750 integration."""
from __future__ import annotations

import logging
from typing import Final

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DolbyCP750Protocol
from .coordinator import DolbyCP750Coordinator

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "dolby_cp750"
DEFAULT_NAME: Final = "Dolby CP750" 
DEFAULT_PORT: Final = 61408

PLATFORMS: list[Platform] = ["select", "number", "switch", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dolby CP750 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    protocol = DolbyCP750Protocol(
        hass,
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get("power_switch")
    )

    coordinator = DolbyCP750Coordinator(
        hass,
        protocol,
        entry.data.get(CONF_NAME, DEFAULT_NAME)
    )

    # Prima connessione e aggiornamento dati iniziale
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "protocol": protocol,
        "host": entry.data[CONF_HOST],
        "port": entry.data.get(CONF_PORT, DEFAULT_PORT),
        "name": entry.data.get(CONF_NAME, DEFAULT_NAME),
        "power_switch": entry.data.get("power_switch"),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok