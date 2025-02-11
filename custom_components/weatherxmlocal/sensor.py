import logging

from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# --- Extraction Helpers ---

def extract_generic(raw, key):
    try:
        if f'"{key}":' in raw:
            part = raw.split(f'"{key}": ')[1]
            value_str = part.split(',')[0].split('}')[0].strip()
            return float(value_str)
    except Exception as e:
        _LOGGER.debug("Error extracting %s: %s", key, e)
    return None

def extract_uv_index(raw):
    try:
        if '"uv_index":' in raw:
            part = raw.split('"uv_index": ')[1]
            value_str = part.split(',')[0].split('}')[0].strip()
            return float(value_str)
    except Exception as e:
        _LOGGER.debug("Error extracting uv_index: %s", e)
    return 0.0

def extract_solar_irradiance(raw):
    try:
        if "Solar rad:" in raw:
            part = raw.split("Solar rad: ")[1]
            value_str = part.split(" ")[0].strip()
            return float(value_str)
    except Exception as e:
        _LOGGER.debug("Error extracting solar irradiance: %s", e)
    return None

def compute_wind_compass(raw):
    wd = extract_generic(raw, "wind_direction")
    if wd is None:
        return "unknown"
    degrees = wd
    if degrees >= 337.5 or degrees < 22.5:
        return "N"
    elif degrees >= 22.5 and degrees < 67.5:
        return "NE"
    elif degrees >= 67.5 and degrees < 112.5:
        return "E"
    elif degrees >= 112.5 and degrees < 157.5:
        return "SE"
    elif degrees >= 157.5 and degrees < 202.5:
        return "S"
    elif degrees >= 202.5 and degrees < 247.5:
        return "SW"
    elif degrees >= 247.5 and degrees < 292.5:
        return "W"
    elif degrees >= 292.5 and degrees < 337.5:
        return "NW"
    else:
        return "unknown"

def compute_wind_speed_knots(raw):
    ws = extract_generic(raw, "wind_speed")
    if ws is None:
        return None
    return round(ws * 1.94384, 2)

# --- Conversion Helpers ---

def convert_temperature(value, unit_system):
    if value is None:
        return None
    if unit_system == "imperial":
        # °C to °F
        return round((value * 9 / 5) + 32, 2)
    return value

def convert_wind_speed(value, unit_system):
    if value is None:
        return None
    if unit_system == "imperial":
        # m/s to mph
        return round(value * 2.23694, 2)
    return value

def convert_precipitation(value, unit_system):
    if value is None:
        return None
    if unit_system == "imperial":
        # mm to inches
        return round(value / 25.4, 2)
    return value

def convert_pressure(value, unit_system):
    if value is None:
        return None
    if unit_system == "imperial":
        # hPa to inHg
        return round(value * 0.02953, 2)
    return value

def convert_precipitation_rate(value, unit_system):
    if value is None:
        return None
    if unit_system == "imperial":
        # mm/h to in/h
        return round(value / 25.4, 2)
    return value

def convert_wind_speed_kmh(raw, unit_system):
    ws = extract_generic(raw, "wind_speed")
    if ws is None:
        return None
    if unit_system == "imperial":
        # m/s to mph (same as wind_speed conversion)
        return round(ws * 2.23694, 2)
    else:
        # m/s to km/h
        return round(ws * 3.6, 2)

# --- Sensor Configuration ---

# Each sensor’s extractor now accepts (raw, unit_system)
SENSOR_CONFIGS = {
    "weatherxm_temperature": {
        "name": "WeatherXM Temperature",
        "extractor": lambda raw, unit_system: convert_temperature(extract_generic(raw, "temperature"), unit_system),
    },
    "weatherxm_humidity": {
        "name": "WeatherXM Humidity",
        "extractor": lambda raw, unit_system: extract_generic(raw, "humidity"),
    },
    "weatherxm_wind_speed": {
        "name": "WeatherXM Wind Speed",
        "extractor": lambda raw, unit_system: convert_wind_speed(extract_generic(raw, "wind_speed"), unit_system),
    },
    "weatherxm_wind_gust": {
        "name": "WeatherXM Wind Gust",
        "extractor": lambda raw, unit_system: convert_wind_speed(extract_generic(raw, "wind_gust"), unit_system),
    },
    "weatherxm_wind_direction": {
        "name": "WeatherXM Wind Direction",
        "extractor": lambda raw, unit_system: extract_generic(raw, "wind_direction"),
    },
    "weatherxm_illuminance": {
        "name": "WeatherXM Illuminance",
        "extractor": lambda raw, unit_system: extract_generic(raw, "illuminance"),
    },
    "weatherxm_solar_irradiance": {
        "name": "WeatherXM Solar Irradiance",
        "extractor": lambda raw, unit_system: extract_solar_irradiance(raw),
    },
    "weatherxm_uv_index": {
        "name": "WeatherXM UV Index",
        "extractor": lambda raw, unit_system: extract_uv_index(raw),
    },
    "weatherxm_precipitation_accumulated": {
        "name": "WeatherXM Precipitation Accumulated",
        "extractor": lambda raw, unit_system: convert_precipitation(extract_generic(raw, "precipitation_accumulated"), unit_system),
    },
    "weatherxm_battery_voltage": {
        "name": "WeatherXM Battery Voltage",
        "extractor": lambda raw, unit_system: extract_generic(raw, "ws_bat_mv"),
    },
    "weatherxm_pressure": {
        "name": "WeatherXM Pressure",
        "extractor": lambda raw, unit_system: convert_pressure(extract_generic(raw, "pressure"), unit_system),
    },
    "weatherxm_precipitation_rate": {
        "name": "WeatherXM Precipitation Rate",
        "extractor": lambda raw, unit_system: convert_precipitation_rate(extract_generic(raw, "precipitation_rate"), unit_system),
    },
    "weatherxm_wind_compass": {
        "name": "WeatherXM Wind Direction Compass",
        "extractor": lambda raw, unit_system: compute_wind_compass(raw),
    },
    "weatherxm_wind_speed_knots": {
        "name": "WeatherXM Wind Speed (Knots)",
        "extractor": lambda raw, unit_system: compute_wind_speed_knots(raw),
    },
    "weatherxm_wind_speed_kmh": {
        "name": "WeatherXM Wind Speed (km/h)",
        "extractor": lambda raw, unit_system: convert_wind_speed_kmh(raw, unit_system),
    },
}

class WeatherXMSensor(SensorEntity):
    """Representation of a WeatherXM sensor."""

    def __init__(self, sensor_id, config):
        self._sensor_id = sensor_id
        self._name = config["name"]
        self._extractor = config["extractor"]
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state if self._state is not None else "unknown"

    @property
    def unit_of_measurement(self):
        # Dynamically adjust the unit based on the unit system option.
        unit_system = self.hass.data.get(DOMAIN, {}).get("unit_system", "metric")
        if self._sensor_id == "weatherxm_temperature":
            return "°F" if unit_system == "imperial" else "°C"
        elif self._sensor_id in ("weatherxm_wind_speed", "weatherxm_wind_gust"):
            return "mph" if unit_system == "imperial" else "m/s"
        elif self._sensor_id == "weatherxm_precipitation_accumulated":
            return "in" if unit_system == "imperial" else "mm"
        elif self._sensor_id == "weatherxm_pressure":
            return "inHg" if unit_system == "imperial" else "hPa"
        elif self._sensor_id == "weatherxm_precipitation_rate":
            return "in/h" if unit_system == "imperial" else "mm/h"
        elif self._sensor_id == "weatherxm_wind_speed_kmh":
            return "mph" if unit_system == "imperial" else "km/h"
        # For other sensors, return None or a fixed unit if desired.
        return None

    @property
    def unique_id(self):
        return self._sensor_id

    def update(self):
        """Fetch new state data for the sensor."""
        data = self.hass.data.get(DOMAIN, {})
        data_reader = data.get("data_reader")
        if data_reader:
            raw = data_reader.get_data()
            unit_system = data.get("unit_system", "metric")
            value = self._extractor(raw, unit_system)
            if value is None:
                self._state = "unknown"
            else:
                self._state = value

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up all WeatherXM sensors."""
    sensors = []
    for sensor_id, sensor_config in SENSOR_CONFIGS.items():
        sensors.append(WeatherXMSensor(sensor_id, sensor_config))
    add_entities(sensors, True)
