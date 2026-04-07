import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SYSTEM_ID,
    CONF_PV_POWER_ENTITY,
    CONF_PV_ENERGY_ENTITY,
    CONF_TEMPERATURE_ENTITY,
    CONF_API_URL,
    CONF_UPLOAD_INTERVAL,
    DEFAULT_UPLOAD_INTERVAL,
    PVOUTPUT_ADDSTATUS_URL,
    ATTR_DATE,
    ATTR_TIME,
    ATTR_ENERGY_GENERATION,
    ATTR_POWER_GENERATION,
    ATTR_TEMPERATURE,
    ATTR_NET_FLAG,
    EVENT_PVOUTPUT_UPLOAD,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the PVOutput Uploader component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PVOutput Uploader from a config entry."""
    system_id = entry.data.get(CONF_SYSTEM_ID)
    _LOGGER.info("Setting up PVOutput System %s", system_id)
    
    # Create device
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[CONF_SYSTEM_ID])},
        name=f"PVOutput System {entry.data[CONF_SYSTEM_ID]}",
        manufacturer="PVOutput",
        model="Uploader",
    )

    uploader = PVOutputUploader(hass, entry, device.id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = uploader

    # Start the periodic upload
    conf = {**entry.data, **entry.options}
    interval = conf.get(CONF_UPLOAD_INTERVAL, DEFAULT_UPLOAD_INTERVAL)
    
    # Trigger first upload right away
    hass.async_create_task(uploader.async_upload())

    entry.async_on_unload(
        async_track_time_interval(
            hass, uploader.async_upload, timedelta(minutes=interval)
        )
    )
    
    # Also listen for option updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    system_id = entry.data.get(CONF_SYSTEM_ID)
    _LOGGER.info("Unloading PVOutput System %s", system_id)
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True

class PVOutputUploader:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device_id: str):
        self.hass = hass
        self.entry = entry
        self.device_id = device_id

    def _get_value(self, entity_id):
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if not state or state.state in ("unknown", "unavailable"):
            return None
        
        try:
            value = float(state.state)
            # Conversion logic based on unit
            unit = state.attributes.get("unit_of_measurement")
            
            # Energy conversion
            if unit == "kWh":
                value *= 1000
            elif unit == "MWh":
                value *= 1000000
            
            # Power conversion
            elif unit == "kW":
                value *= 1000
            elif unit == "MW":
                value *= 1000000
            
            # Temperature conversion (PVOutput expects Celsius)
            if unit in ("°F", "F"):
                value = (value - 32) * 5 / 9
            
            return value
        except ValueError:
            return None

    async def async_upload(self, _now=None):
        """Upload data to PVOutput."""
        conf = {**self.entry.data, **self.entry.options}
        
        api_key = conf.get(CONF_API_KEY)
        system_id = conf.get(CONF_SYSTEM_ID)
        pv_power_entity = conf.get(CONF_PV_POWER_ENTITY)
        pv_energy_entity = conf.get(CONF_PV_ENERGY_ENTITY)
        temperature_entity = conf.get(CONF_TEMPERATURE_ENTITY)
        api_url = conf.get(CONF_API_URL)

        now = dt_util.now()
        
        pv_power = self._get_value(pv_power_entity)
        pv_energy = self._get_value(pv_energy_entity)
        
        if pv_power is None and pv_energy is None:
            _LOGGER.warning("Skipping upload: both power and energy entities are unavailable for System %s", system_id)
            self.hass.bus.async_fire(
                EVENT_PVOUTPUT_UPLOAD,
                {
                    "device_id": self.device_id,
                    "message": "Skipping upload: both power and energy entities are unavailable",
                },
            )
            return

        payload = {
            ATTR_DATE: now.strftime("%Y%m%d"),
            ATTR_TIME: now.strftime("%H:%M"),
        }
        
        if pv_energy is not None:
            payload[ATTR_ENERGY_GENERATION] = int(pv_energy)
            payload[ATTR_NET_FLAG] = 1
        if pv_power is not None:
            payload[ATTR_POWER_GENERATION] = int(pv_power)
            
        if temperature_entity:
            temperature_value = self._get_value(temperature_entity)
            if temperature_value is not None:
                payload[ATTR_TEMPERATURE] = f"{temperature_value:.1f}"

        url = api_url if api_url else PVOUTPUT_ADDSTATUS_URL
        headers = {
            "X-Pvoutput-Apikey": api_key,
            "X-Pvoutput-SystemId": system_id,
        }

        
        payload_str = f"payload={{{','.join(f'{k}={v}' for k, v in payload.items())}}}"
        _LOGGER.debug("Uploading to PVOutput (%s): %s", url, payload)

        try:
            session = async_get_clientsession(self.hass)
            async with session.post(url, data=payload, headers=headers, timeout=10) as response:
                if response.status == 200:
                    _LOGGER.info(f"Uploaded {payload_str} (System={system_id})")
                    # Log activity to UI Logbook
                    self.hass.bus.async_fire(
                        EVENT_PVOUTPUT_UPLOAD,
                        {
                            "device_id": self.device_id,
                            "message": f"Uploaded: {payload_str}",
                        },
                    )
                else:
                    text = await response.text()
                    error_message = f"Failed to upload: {response.status} {text} = {payload_str}"
                    _LOGGER.error(error_message)
                    # Log failure activity to UI Logbook
                    self.hass.bus.async_fire(
                        EVENT_PVOUTPUT_UPLOAD,
                        {
                            "device_id": self.device_id,
                            "message": error_message,
                        },
                    )
        except Exception as ex:
            error_message = f"Error={ex} with payload: {payload_str}"
            _LOGGER.error(error_message)
            self.hass.bus.async_fire(
                EVENT_PVOUTPUT_UPLOAD,
                {
                    "device_id": self.device_id,
                    "message": error_message,
                },
            )
