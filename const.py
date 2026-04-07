DOMAIN = "pvoutput_uploader"

CONF_API_KEY = "api_key"
CONF_SYSTEM_ID = "system_id"
CONF_PV_POWER_ENTITY = "pv_power_entity"
CONF_PV_ENERGY_ENTITY = "pv_energy_entity"
CONF_TEMPERATURE_ENTITY = "temperature_entity"
CONF_API_URL = "api_url"
CONF_UPLOAD_INTERVAL = "upload_interval"

DEFAULT_UPLOAD_INTERVAL = 5 # minutes

PVOUTPUT_ADDSTATUS_URL = "https://pvoutput.org/service/r2/addstatus.jsp"

# Attributes for PVOutput
ATTR_DATE = "d"
ATTR_TIME = "t"
ATTR_ENERGY_GENERATION = "v1"
ATTR_POWER_GENERATION = "v2"
ATTR_TEMPERATURE = "v5"

EVENT_PVOUTPUT_UPLOAD = f"{DOMAIN}_upload"
