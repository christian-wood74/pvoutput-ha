"""Describe pvoutput_uploader logbook events."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.logbook import LOGBOOK_ENTRY_MESSAGE, LOGBOOK_ENTRY_NAME
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, EVENT_PVOUTPUT_UPLOAD


@callback
def async_describe_events(
        hass: HomeAssistant,
        async_describe_event: Callable[[str, str, Callable[[Event], dict[str, str]]], None],
) -> None:
    """Describe logbook events."""
    device_registry = dr.async_get(hass)

    @callback
    def async_describe_logbook_event(event: Event) -> dict[str, str]:
        """Describe logbook event."""
        device_id = event.data.get(ATTR_DEVICE_ID)
        device_name = "PVOutput System"

        if device_id:
            device = device_registry.async_get(device_id)
            if device:
                device_name = device.name_by_user or device.name or device_name

        message = event.data.get("message", "Uploaded data to PVOutput")

        return {
            LOGBOOK_ENTRY_NAME: device_name,
            LOGBOOK_ENTRY_MESSAGE: message,
        }

    async_describe_event(DOMAIN, EVENT_PVOUTPUT_UPLOAD, async_describe_logbook_event)
