import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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
)

class PVOutputConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PVOutput Uploader."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        self._data = {}

    async def async_step_user(self, user_input=None):
        """First step: API info."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_SYSTEM_ID])
            self._abort_if_unique_id_configured()
            self._data.update(user_input)
            return await self.async_step_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Required(CONF_SYSTEM_ID): str,
                }
            ),
            errors=errors,
        )

    async def async_step_entities(self, user_input=None):
        """Second step: Select entities"""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=f"PVOutput System {self._data[CONF_SYSTEM_ID]}",
                data=self._data,
            )

        return self.async_show_form(
            step_id="entities",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PV_POWER_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="power")
                    ),
                    vol.Required(CONF_PV_ENERGY_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="energy")
                    ),
                    vol.Optional(CONF_TEMPERATURE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Optional(CONF_API_URL): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                    ),
                    vol.Required(
                        CONF_UPLOAD_INTERVAL, default=DEFAULT_UPLOAD_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return PVOutputOptionsFlowHandler()

class PVOutputOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for PVOutput Uploader."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        conf = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PV_POWER_ENTITY,
                        default=conf.get(CONF_PV_POWER_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="power")
                    ),
                    vol.Required(
                        CONF_PV_ENERGY_ENTITY,
                        default=conf.get(CONF_PV_ENERGY_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="energy")
                    ),
                    vol.Optional(
                        CONF_TEMPERATURE_ENTITY,
                        default=conf.get(CONF_TEMPERATURE_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Optional(
                        CONF_API_URL,
                        default=conf.get(CONF_API_URL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.URL)
                    ),
                    vol.Required(
                        CONF_UPLOAD_INTERVAL,
                        default=conf.get(CONF_UPLOAD_INTERVAL, DEFAULT_UPLOAD_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
        )
