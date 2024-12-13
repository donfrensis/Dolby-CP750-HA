"""Config flow for Dolby CP750 integration."""
from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_SWITCHES,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DolbyCP750Protocol

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 61408
DEFAULT_NAME = "Dolby CP750"

class DolbyCP750ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dolby CP750."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data = {}

    async def _test_connection(self, host: str, port: int) -> bool:
        """Test if we can connect to the CP750."""
        try:
            protocol = DolbyCP750Protocol(host, port)
            await protocol.connect()
            await protocol.disconnect()
            return True
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Test the connection
            if await self._test_connection(user_input[CONF_HOST], user_input[CONF_PORT]):
                self._data.update(user_input)
                # Proceed to power switch selection
                return await self.async_step_power_switch()
            
            errors["base"] = "cannot_connect"

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                }
            ),
            errors=errors,
        )

    async def async_step_power_switch(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle power switch selection."""
        if user_input is not None:
            if "power_switch" in user_input:
                self._data["power_switch"] = user_input["power_switch"]
            
            # Create the config entry
            return self.async_create_entry(
                title=self._data[CONF_NAME],
                data=self._data,
            )

        # Get list of available switches
        switch_entities = self.hass.states.async_entity_ids("switch")
        
        return self.async_show_form(
            step_id="power_switch",
            data_schema=vol.Schema(
                {
                    vol.Optional("power_switch"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="switch",
                            multiple=False,
                        ),
                    ),
                }
            ),
            description_placeholders={
                "switches_available": str(len(switch_entities)),
            },
        )