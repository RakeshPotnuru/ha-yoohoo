"""Set up Yoohoo by pasting a source's link from the Yoohoo app."""

from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import CannotConnect, LinkGone, async_post, build_payload
from .const import CONF_URL, DOMAIN, LINK_PATTERN

DATA_SCHEMA = vol.Schema({vol.Required(CONF_URL): TextSelector(TextSelectorConfig(type=TextSelectorType.URL))})


class YoohooConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for the link, check it with a test alert, and save it."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """The only step: paste the link."""
        errors: dict[str, str] = {}
        if user_input is not None:
            link = user_input[CONF_URL].strip()
            if not LINK_PATTERN.match(link):
                errors["base"] = "invalid_link"
            else:
                # The link is private, so the entry is keyed by a hash of it, never the link itself.
                await self.async_set_unique_id(hashlib.sha256(link.rstrip("/").encode()).hexdigest()[:32])
                self._abort_if_unique_id_configured()
                try:
                    await async_post(
                        self.hass,
                        link,
                        build_payload("Home Assistant connected", "Alerts from your Home Assistant automations will show up here."),
                    )
                except LinkGone:
                    errors["base"] = "link_gone"
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title="Yoohoo", data={CONF_URL: link})
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
