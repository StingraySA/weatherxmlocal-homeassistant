"""WeatherXM Local Sensors."""
import json
import serial
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, PERCENTAGE, SPEED_METERS_PER_SECOND

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "temperature": {"name": "Temperature", "unit_metric": UnitOfTemperature.CELSIUS, "unit_imperial": UnitOfTemperature.FAHRENHEIT},
    "humidity": {"name": "Humidity", "unit_metric": PERCENTAGE, "unit_imperial": PERCENTAGE},
    "wind_speed": {"name": "Wind Speed", "unit_metric": SPEED_METERS_PER_SECOND, "unit_imperial": "mph"},
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up WeatherXM Local sensors from a config entry."""
    serial_port = entry.data["serial_port"]
    unit_system = entry.data["unit_system"]

    async_add_entities([WeatherXMSensor(serial_port, key, unit_system) for key in SENSOR_TYPES], True)

class WeatherXMSensor(SensorEntity):
    """Representation of a WeatherXM Sensor."""

    def __init__(self, serial_port, sensor_type, unit_system):
        """Initialize the sensor."""
        self._serial_port = serial_port
        self._sensor_type = sensor_type
        self._attr_name = f"WeatherXM {SENSOR_TYPES[sensor_type]['name']}"
        self._unit_system = unit_system
        self._attr_unit_of_measurement = SENSOR_TYPES[sensor_type][f"unit_{unit_system}"]
        self._attr_state = None

    def update(self):
        """Fetch data from the serial port."""
        try:
            with serial.Serial(self._serial_port, 115200, timeout=1) as ser:
                raw_data = ser.readline().decode("utf-8").strip()
                parsed_data = json.loads(raw_data)
                self._attr_state = parsed_data.get(self._sensor_type, "unknown")
        except Exception as e:
            _LOGGER.error("Error reading serial data: %s", e)
