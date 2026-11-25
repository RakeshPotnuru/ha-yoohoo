"""Posts alerts to a Yoohoo custom webhook link."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LEVELS, TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)


class YoohooError(Exception):
    """Yoohoo could not take the alert."""


class CannotConnect(YoohooError):
    """Yoohoo could not be reached, or answered with an error."""


class LinkGone(YoohooError):
    """The link no longer belongs to a source: it was deleted or a new link was made."""


def build_payload(
    title: str,
    message: str | None = None,
    level: str = "roundup",
    group: str | None = None,
    url: str | None = None,
) -> dict[str, Any]:
    """The JSON Yoohoo's custom webhook reads. Each alert carries its own id, so a retry is never shown twice."""
    payload: dict[str, Any] = {
        "id": uuid.uuid4().hex,
        "title": title[:120],
        "status": LEVELS.get(level, LEVELS["roundup"]),
    }
    if message:
        payload["message"] = message[:600]
    if group:
        payload["group"] = group[:80]
    if url:
        payload["url"] = url
    return payload


async def async_post(hass: HomeAssistant, link: str, payload: dict[str, Any]) -> bool:
    """Post one alert. Returns False when the source is paused on Yoohoo's free plan, which drops it."""
    session = async_get_clientsession(hass)
    try:
        async with asyncio.timeout(TIMEOUT_SECONDS), session.post(link, json=payload) as response:
            if response.status in (401, 404, 410):
                raise LinkGone
            if response.status >= 400:
                raise CannotConnect(f"Yoohoo answered {response.status}")
            body = await response.json(content_type=None)
    except YoohooError:
        raise
    except (aiohttp.ClientError, TimeoutError, ValueError) as err:
        raise CannotConnect(str(err) or type(err).__name__) from err
    return not (isinstance(body, dict) and body.get("paused"))


def link_gone_issue_id(entry_id: str) -> str:
    """One repair issue per entry for a link that stopped working."""
    return f"link_gone_{entry_id}"


async def async_send_alert(hass: HomeAssistant, entry_id: str, link: str, payload: dict[str, Any]) -> None:
    """Send an alert without failing the automation that sent it. Problems go to the log and to Repairs."""
    try:
        accepted = await async_post(hass, link, payload)
    except LinkGone:
        _LOGGER.warning("Yoohoo no longer knows this link, so the alert %r was not sent", payload["title"])
        ir.async_create_issue(
            hass,
            DOMAIN,
            link_gone_issue_id(entry_id),
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            translation_key="link_gone",
        )
        return
    except CannotConnect as err:
        _LOGGER.warning("Couldn't send the alert %r to Yoohoo: %s", payload["title"], err)
        return
    ir.async_delete_issue(hass, DOMAIN, link_gone_issue_id(entry_id))
    if not accepted:
        _LOGGER.warning(
            "Yoohoo paused this source because the account has more sources than its plan allows, "
            "so the alert %r was dropped. Pick which sources run in the Yoohoo app",
            payload["title"],
        )
