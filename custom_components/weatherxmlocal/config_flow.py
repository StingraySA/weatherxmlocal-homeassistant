import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PORT

from .const import DOMAIN, DEFAULT_SERIAL_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT_SYSTEM

DATA_SCHEMA = vol.Schema({
    vol.Required("serial_port", default=DEFAULT_SERIAL_PORT): str,
    vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
    vol.Required("unit_system", default=DEFAULT_UNIT_SYSTEM): vol.In(["metric", "imperial"]),
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # (Optional: Validate serial connection here)
            return self.async_create_entry(title="WeatherXM Local", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
