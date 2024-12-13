"""Constants and protocol handler for the Dolby CP750."""
import asyncio
from typing import Final

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

# Services
SERVICE_SET_INPUT = "set_input"
SERVICE_SET_FADER = "set_fader"
SERVICE_SET_MUTE = "set_mute"

# Attributes
ATTR_FADER = "fader"
ATTR_INPUT = "input"
ATTR_MUTE = "mute"
ATTR_POWER = "power"
ATTR_CONNECTED = "connected"

class DolbyCP750Protocol:
    """Protocol handler for Dolby CP750."""

    def __init__(self, host: str, port: int):
        """Initialize the protocol handler."""
        self.host = host
        self.port = port
        self._reader = None
        self._writer = None

    async def connect(self) -> None:
        """Establish connection to the device."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=2.0
            )
        except Exception as err:
            raise ConnectionError(f"Failed to connect: {err}")

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None

    async def send_command(self, command: str) -> str:
        """Send command and return response."""
        if not self._writer:
            await self.connect()

        try:
            self._writer.write(f"{command}\r\n".encode())
            await self._writer.drain()
            response = await asyncio.wait_for(self._reader.readline(), timeout=2.0)
            return response.decode().strip()
        except Exception as err:
            await self.disconnect()
            raise ConnectionError(f"Command failed: {err}")