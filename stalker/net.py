"""Shared HTTP session."""

from __future__ import annotations

import requests

from stalker import __version__

DEFAULT_TIMEOUT = 10

# A regular browser User-Agent: many sites answer bare scripts with 403 or a captcha page.
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
TOOL_UA = f"stalker/{__version__} (+https://github.com/xkudcobi/stalker)"


def session(browser: bool = False) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": BROWSER_UA if browser else TOOL_UA,
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return s


class StalkerError(Exception):
    """A lookup failed for a reason we can show to the user.

    `key` is an i18n key; `params` are its format arguments.
    """

    def __init__(self, key: str, **params):
        super().__init__(key)
        self.key = key
        self.params = params
