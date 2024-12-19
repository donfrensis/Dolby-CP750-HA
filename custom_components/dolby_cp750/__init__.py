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

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "dolby_cp750"
DEFAULT_NAME: Final = "Dolby CP750"
DEFAULT_PORT: Final = 61408

# Definiamo le piattaforme utilizzate dall'integrazione
PLATFORMS: list[Platform] = ["select", "number", "switch", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dolby CP750 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create protocol and coordinator
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
    
    # Memorizza i dati di configurazione
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "host": entry.data[CONF_HOST],
        "port": entry.data.get(CONF_PORT, DEFAULT_PORT),
        "name": entry.data.get(CONF_NAME, DEFAULT_NAME),
        "power_switch": entry.data.get("power_switch"),  # Opzionale
    }

    # Carica le piattaforme
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Scarica le piattaforme
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Rimuove i dati dell'entry
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok