"""Test the Dolby CP750 entity."""
from unittest.mock import patch, AsyncMock
import pytest

from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant

from custom_components.dolby_cp750.const import DolbyCP750Protocol
from custom_components.dolby_cp750.entity import DolbyCP750Entity

@pytest.fixture
def mock_protocol():
    """Create a mock protocol."""
    protocol = DolbyCP750Protocol("192.168.1.100", 61408)
    protocol.send_command = AsyncMock(return_value="cp750.sys.fader 0.0")
    return protocol

async def test_entity_state(hass: HomeAssistant, mock_protocol) -> None:
    """Test entity state updates."""
    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=mock_protocol,
        power_switch=None,
        unique_id="test",
    )

    # Test initial state
    assert entity.state == STATE_OFF

    # Mock successful connection
    mock_protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]

    await entity.async_update()
    assert entity.state == STATE_ON
    assert entity.extra_state_attributes["fader"] == 0.0
    assert entity.extra_state_attributes["mute"] is False

async def test_entity_commands(hass: HomeAssistant, mock_protocol) -> None:
    """Test entity commands."""
    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=mock_protocol,
        power_switch=None,
        unique_id="test",
    )

    # Set up initial state
    mock_protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    await entity.async_update()

    # Test set_fader
    mock_protocol.send_command.reset_mock()
    mock_protocol.send_command.side_effect = [
        "cp750.sys.fader -10.0",
        "cp750.sys.fader -10.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    await entity.async_set_fader(-10.0)
    assert entity.extra_state_attributes["fader"] == -10.0