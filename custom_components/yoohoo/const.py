"""Constants for the Yoohoo integration."""

from __future__ import annotations

import re
from typing import Final

DOMAIN: Final = "yoohoo"

CONF_URL: Final = "url"

# A Yoohoo custom webhook link: <supabase>/functions/v1/webhook/<64 hex characters>.
LINK_PATTERN: Final = re.compile(r"^https?://[^\s/]+(?:/[^\s]*)?/webhook/[a-f0-9]{64}/?$")

# Each level is a `status` word Yoohoo's custom webhook understands (customStatus in
# packages/shared/src/webhook.ts). The Shortcuts action sends the same words.
LEVELS: Final = {
    "roundup": "info",
    "needs_me": "waiting",
    "wrong": "failed",
    "all_good": "ok",
}
DEFAULT_LEVEL: Final = "roundup"

ATTR_CONFIG_ENTRY_ID: Final = "config_entry_id"
ATTR_TITLE: Final = "title"
ATTR_MESSAGE: Final = "message"
ATTR_LEVEL: Final = "level"
ATTR_GROUP: Final = "group"
ATTR_URL: Final = "url"

SERVICE_SEND_ALERT: Final = "send_alert"

TIMEOUT_SECONDS: Final = 10
