"""Send Home Assistant alerts to Yoohoo: the ones that matter now, the rest at the evening roundup."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import async_send_alert, build_payload
from .const import (
    ATTR_CONFIG_ENTRY_ID,
    ATTR_GROUP,
    ATTR_LEVEL,
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_URL,
    CONF_URL,
    DEFAULT_LEVEL,
    DOMAIN,
    LEVELS,
    SERVICE_SEND_ALERT,
)

PLATFORMS: list[Platform] = [Platform.NOTIFY]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type YoohooConfigEntry = ConfigEntry[str]

SEND_ALERT_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_TITLE): cv.string,
        vol.Optional(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_LEVEL, default=DEFAULT_LEVEL): vol.In(list(LEVELS)),
        vol.Optional(ATTR_GROUP): cv.string,
        vol.Optional(ATTR_URL): cv.url,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the Send alert action once, for every Yoohoo entry."""

    async def send_alert(call: ServiceCall) -> None:
        entry = _entry_for(hass, call.data.get(ATTR_CONFIG_ENTRY_ID))
        payload = build_payload(
            call.data[ATTR_TITLE],
            call.data.get(ATTR_MESSAGE),
            call.data[ATTR_LEVEL],
            call.data.get(ATTR_GROUP),
            call.data.get(ATTR_URL),
        )
        await async_send_alert(hass, entry.entry_id, entry.runtime_data, payload)

    hass.services.async_register(DOMAIN, SERVICE_SEND_ALERT, send_alert, schema=SEND_ALERT_SCHEMA)
    return True


def _entry_for(hass: HomeAssistant, entry_id: str | None) -> YoohooConfigEntry:
    """The chosen Yoohoo entry, or the only loaded one when none is chosen."""
    loaded = [e for e in hass.config_entries.async_entries(DOMAIN) if e.state is ConfigEntryState.LOADED]
    if entry_id:
        for entry in loaded:
            if entry.entry_id == entry_id:
                return entry
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="entry_not_found")
    if not loaded:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_set_up")
    if len(loaded) > 1:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="pick_entry")
    return loaded[0]


async def async_setup_entry(hass: HomeAssistant, entry: YoohooConfigEntry) -> bool:
    """Keep the link on the entry and add the notify entity."""
    entry.runtime_data = entry.data[CONF_URL]
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: YoohooConfigEntry) -> bool:
    """Remove the notify entity."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
