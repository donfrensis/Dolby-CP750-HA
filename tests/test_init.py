"""Test the Dolby CP750 integration."""
from unittest.mock import patch
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from custom_components.dolby_cp750 import (
    async_setup_entry,
    async_unload_entry,
    DOMAIN,
    DEFAULT_PORT,
    DEFAULT_NAME,
)

@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock config entry."""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="Test CP750",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
            CONF_NAME: DEFAULT_NAME,
        },
        source="test",
        entry_id="test",
        unique_id="test",
    )

async def test_setup_entry(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> None:
    """Test setting up the integration."""
    with patch(
        "custom_components.dolby_cp750.DolbyCP750Protocol.connect",
        return_value=None,
    ):
        assert await async_setup_entry(hass, mock_config_entry)
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]

async def test_unload_entry(hass: HomeAssistant, mock_config_entry: ConfigEntry) -> None:
    """Test unloading the integration."""
    with patch(
        "custom_components.dolby_cp750.DolbyCP750Protocol.connect",
        return_value=None,
    ):
        await async_setup_entry(hass, mock_config_entry)
        assert await async_unload_entry(hass, mock_config_entry)
        assert mock_config_entry.entry_id not in hass.data[DOMAIN]