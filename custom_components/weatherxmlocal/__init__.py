import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType

DOMAIN = "weatherxmlocal"
PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the WeatherXM Local integration."""
    return True

def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WeatherXM Local from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload WeatherXM Local config entry."""
    return hass.config_entries.async_unload_platforms(entry, PLATFORMS)