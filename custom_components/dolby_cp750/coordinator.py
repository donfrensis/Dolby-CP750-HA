"""Data update coordinator for Dolby CP750."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from .const import DOMAIN, DolbyCP750Protocol

_LOGGER = logging.getLogger(__name__)

class DolbyCP750Coordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Dolby CP750."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        protocol: DolbyCP750Protocol,
        name: str
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} Coordinator",
            update_interval=timedelta(seconds=1),
        )
        self.protocol = protocol
        self.data = {}

    async def _async_update_data(self):
        """Fetch data from CP750."""
        # Prima controlla se il dispositivo è acceso
        if not await self.protocol._check_power_switch():
            # Se è spento, restituisci None per tutti i valori senza generare errori
            return {
                "fader": None,
                "input": None,
                "mute": None,
                "dig_1_valid": None,
                "dig_2_valid": None,
                "dig_3_valid": None,
                "dig_4_valid": None,
            }

        try:
            # Se è acceso, procedi con il normale aggiornamento
            fader = await self.protocol.send_command("cp750.sys.fader ?")
            input_mode = await self.protocol.send_command("cp750.sys.input_mode ?")
            mute = await self.protocol.send_command("cp750.sys.mute ?")

            data = {
                "fader": float(fader.split()[1]) if len(fader.split()) >= 2 else None,
                "input": input_mode.split()[1] if len(input_mode.split()) >= 2 else None,
                "mute": mute.split()[1] == "1" if len(mute.split()) >= 2 else None,
            }

            for i in range(1, 5):
                response = await self.protocol.send_command(f"cp750.state.dig_{i}_valid ?")
                data[f"dig_{i}_valid"] = response.split()[1] == "1" if len(response.split()) >= 2 else None

            return data
        except Exception as err:
            _LOGGER.debug("Error updating data: %s", err)  # Cambiato da error a debug
            raise