"""Test Dolby CP750 translations."""
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.dolby_cp750.const import DOMAIN

async def test_config_flow_translations(hass: HomeAssistant) -> None:
    """Test translations in config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    # Verifica il titolo del form
    assert result["data_schema"].schema["host"].title == "IP Address"
    assert result["data_schema"].schema["port"].title == "Port"
    
    # Verifica messaggio di errore
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "invalid_ip",
            "port": 61408,
            "name": "Test CP750",
        },
    )
    assert result2["errors"]["base"] == "cannot_connect"

async def test_service_translations(hass: HomeAssistant) -> None:
    """Test service description translations."""
    # Verifica descrizioni servizi
    services = await hass.services.async_services()
    if DOMAIN in services:
        assert services[DOMAIN]["set_fader"]["description"] is not None
        assert services[DOMAIN]["set_input"]["description"] is not None
        assert services[DOMAIN]["set_mute"]["description"] is not None