"""Extended tests for the Dolby CP750 entity."""
import asyncio
from unittest.mock import patch, AsyncMock
import pytest

from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.core import HomeAssistant

from custom_components.dolby_cp750.const import DolbyCP750Protocol, INPUT_SOURCES
from custom_components.dolby_cp750.entity import DolbyCP750Entity

async def test_entity_with_power_switch(hass: HomeAssistant) -> None:
    """Test entity behavior with power switch."""
    protocol = DolbyCP750Protocol("192.168.1.100", 61408)
    protocol.send_command = AsyncMock()

    # Create entity with power switch
    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=protocol,
        power_switch="switch.cp750_power",
        unique_id="test",
    )

    # Test with power switch OFF
    hass.states.async_set("switch.cp750_power", STATE_OFF)
    await entity.async_update()
    assert entity.state == STATE_OFF
    assert not protocol.send_command.called

    # Test with power switch ON
    protocol.send_command.reset_mock()
    protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    
    hass.states.async_set("switch.cp750_power", STATE_ON)
    await entity.async_update()
    assert entity.state == STATE_ON
    assert protocol.send_command.called

async def test_connection_errors(hass: HomeAssistant) -> None:
    """Test handling of connection errors."""
    protocol = DolbyCP750Protocol("192.168.1.100", 61408)
    protocol.send_command = AsyncMock()

    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=protocol,
        power_switch=None,
        unique_id="test",
    )

    # Test timeout
    protocol.send_command.side_effect = asyncio.TimeoutError()
    await entity.async_update()
    assert entity.state == STATE_OFF

    # Test connection error
    protocol.send_command.side_effect = ConnectionError()
    await entity.async_update()
    assert entity.state == STATE_OFF

    # Test recovery after error
    protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    await entity.async_update()
    assert entity.state == STATE_ON

async def test_input_source_changes(hass: HomeAssistant) -> None:
    """Test changing input sources."""
    protocol = DolbyCP750Protocol("192.168.1.100", 61408)
    protocol.send_command = AsyncMock()

    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=protocol,
        power_switch=None,
        unique_id="test",
    )

    # Set up initial state
    protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    await entity.async_update()

    # Test each input source
    for internal_source, display_name in INPUT_SOURCES.items():
        protocol.send_command.reset_mock()
        protocol.send_command.side_effect = [
            f"cp750.sys.input_mode {internal_source}",
            f"cp750.sys.input_mode {internal_source}",
            "cp750.sys.fader 0.0",
            "cp750.sys.mute 0",
        ]
        
        await entity.async_set_input(display_name)
        assert entity.extra_state_attributes["input"] == display_name
        assert protocol.send_command.call_count > 0

async def test_fader_limits(hass: HomeAssistant) -> None:
    """Test fader value limits and validation."""
    protocol = DolbyCP750Protocol("192.168.1.100", 61408)
    protocol.send_command = AsyncMock()

    entity = DolbyCP750Entity(
        name="Test CP750",
        protocol=protocol,
        power_switch=None,
        unique_id="test",
    )

    # Setup initial state
    protocol.send_command.side_effect = [
        "cp750.sys.fader 0.0",
        "cp750.sys.input_mode dig_1",
        "cp750.sys.mute 0",
    ]
    await entity.async_update()

    # Test valid fader values
    test_values = [-90.0, -45.0, 0.0, 5.0, 10.0]
    for value in test_values:
        protocol.send_command.reset_mock()
        protocol.send_command.side_effect = [
            f"cp750.sys.fader {value}",
            f"cp750.sys.fader {value}",
            "cp750.sys.input_mode dig_1",
            "cp750.sys.mute 0",
        ]
        
        await entity.async_set_fader(value)
        assert entity.extra_state_attributes["fader"] == value