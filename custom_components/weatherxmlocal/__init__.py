import logging
import threading
import time
import serial

from .const import DOMAIN, DEFAULT_SERIAL_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT_SYSTEM

_LOGGER = logging.getLogger(__name__)

# Data reading class that polls the serial port.
class WeatherXMData:
    def __init__(self, serial_port, scan_interval):
        self.serial_port = serial_port
        self._scan_interval = scan_interval
        self._data = ""
        self._lock = threading.Lock()
        self._stop_thread = False
        self.thread = threading.Thread(target=self._read_serial, daemon=True)

    def start_reading(self):
        self.thread.start()

    def stop_reading(self):
        self._stop_thread = True
        self.thread.join()

    def _read_serial(self):
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
        except Exception as e:
            _LOGGER.error("Failed to open serial port %s: %s", self.serial_port, e)
            return

        while not self._stop_thread:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    with self._lock:
                        self._data = line
            except Exception as e:
                _LOGGER.error("Error reading from serial port: %s", e)
            time.sleep(self._scan_interval)

    def get_data(self):
        with self._lock:
            return self._data

# --- Config Entry Setup ---

async def async_setup_entry(hass, entry):
    """Set up WeatherXM Local from a config entry."""
    serial_port = entry.data.get("serial_port", DEFAULT_SERIAL_PORT)
    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    unit_system = entry.data.get("unit_system", DEFAULT_UNIT_SYSTEM)

    data_reader = WeatherXMData(serial_port, scan_interval)
    data_reader.start_reading()

    # Store both the data reader and configuration options
    hass.data.setdefault(DOMAIN, {})["data_reader"] = data_reader
    hass.data[DOMAIN]["unit_system"] = unit_system
    hass.data[DOMAIN]["scan_interval"] = scan_interval

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    data = hass.data.get(DOMAIN, {})
    data_reader = data.get("data_reader")
    if data_reader:
        data_reader.stop_reading()
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
