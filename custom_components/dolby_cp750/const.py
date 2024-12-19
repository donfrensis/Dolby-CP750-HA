"""Constants and protocol handler for the Dolby CP750."""
import asyncio
import logging
from typing import Final, Optional

from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Domain
DOMAIN: Final = "dolby_cp750"

# Available input sources
INPUT_SOURCES: Final = {
    "dig_1": "Digital 1",
    "dig_2": "Digital 2",
    "dig_3": "Digital 3",
    "dig_4": "Digital 4",
    "analog": "Multi-Ch Analog",
    "non_sync": "NonSync",
    "mic": "Mic",
}

class DolbyCP750Protocol:
    """Protocol handler for Dolby CP750."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, power_switch: Optional[str] = None):
        """Initialize the protocol handler."""
        self.hass = hass
        self.host = host
        self.port = port
        self._power_switch = power_switch
        self._reader = None
        self._writer = None
        self._connected = False

    async def _check_power_switch(self) -> bool:
        """Check if power switch is on (if configured)."""
        if not self._power_switch:
            return True  # No switch configured, assume powered
        
        power_state = self.hass.states.get(self._power_switch)
        if not power_state:
            _LOGGER.warning("Configured power switch %s not found", self._power_switch)
            return True  # Switch not found, assume powered
        
        return power_state.state == STATE_ON

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self._connected

    async def connect(self) -> None:
        """Establish connection to the device."""
        # First check power switch if configured
        if not await self._check_power_switch():
            self._connected = False
            raise ConnectionError("Device is powered off")

        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=2.0
            )
            self._connected = True
        except Exception as err:
            self._connected = False
            raise ConnectionError(f"Failed to connect: {err}")

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None
        self._connected = False

    async def send_command(self, command: str) -> str:
        """Send command and return response."""
        # First check power
        if not await self._check_power_switch():
            self._connected = False
            raise ConnectionError("Device is powered off")

        if not self._writer:
            await self.connect()

        try:
            self._writer.write(f"{command}\r\n".encode())
            await self._writer.drain()
            response = await asyncio.wait_for(self._reader.readline(), timeout=2.0)
            self._connected = True
            return response.decode().strip()
        except Exception as err:
            self._connected = False
            await self.disconnect()
            raise ConnectionError(f"Command failed: {err}")