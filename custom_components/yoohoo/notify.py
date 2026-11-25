"""A Yoohoo notify entity, for anything that sends with notify.send_message. Its alerts wait for the roundup."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import YoohooConfigEntry
from .api import async_send_alert, build_payload
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: YoohooConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add one notify entity per Yoohoo entry."""
    async_add_entities([YoohooNotifyEntity(entry)])


class YoohooNotifyEntity(NotifyEntity):
    """Sends a message to Yoohoo for the evening roundup."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = NotifyEntityFeature.TITLE

    def __init__(self, entry: YoohooConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Yoohoo",
            manufacturer="Yoohoo",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://yoohoo.buzz",
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """With a title, the message goes under it. Without one, the message is the title."""
        payload = build_payload(title, message) if title else build_payload(message)
        await async_send_alert(self.hass, self._entry.entry_id, self._entry.runtime_data, payload)
