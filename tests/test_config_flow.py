"""Test the Dolby CP750 config flow."""
from unittest.mock import patch
import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.dolby_cp750.const import DOMAIN
from custom_components.dolby_cp750.config_flow import DolbyCP750ConfigFlow

async def test_config_flow_complete(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    # Test submit with connection success
    with patch(
        "custom_components.dolby_cp750.config_flow.DolbyCP750ConfigFlow._test_connection",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 61408,
                CONF_NAME: "Test CP750",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "power_switch"

    # Complete setup without power switch
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {},
    )

    assert result3["type"] == FlowResultType.CREATE_ENTRY
    assert result3["title"] == "Test CP750"
    assert result3["data"] == {
        CONF_HOST: "192.168.1.100",
        CONF_PORT: 61408,
        CONF_NAME: "Test CP750",
    }

async def test_config_flow_with_power_switch(hass: HomeAssistant) -> None:
    """Test config flow with power switch selection."""
    # Create a mock switch state
    hass.states.async_set("switch.cp750_power", "on")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Test submit with connection success
    with patch(
        "custom_components.dolby_cp750.config_flow.DolbyCP750ConfigFlow._test_connection",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 61408,
                CONF_NAME: "Test CP750",
            },
        )

    # Complete setup with power switch
    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            "power_switch": "switch.cp750_power",
        },
    )

    assert result3["type"] == FlowResultType.CREATE_ENTRY
    assert result3["data"]["power_switch"] == "switch.cp750_power"

async def test_config_flow_connection_failed(hass: HomeAssistant) -> None:
    """Test we handle failed connection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.dolby_cp750.config_flow.DolbyCP750ConfigFlow._test_connection",
        return_value=False,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: 61408,
                CONF_NAME: "Test CP750",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"]["base"] == "cannot_connect"