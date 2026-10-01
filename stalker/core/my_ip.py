"""Discover the caller's public IPv4 / IPv6 addresses."""

from __future__ import annotations

import ipaddress

import requests

from stalker.net import StalkerError, session

IPV4_SOURCES = ("https://api.ipify.org", "https://ipv4.icanhazip.com", "https://v4.ident.me")
IPV6_SOURCES = ("https://api6.ipify.org", "https://ipv6.icanhazip.com", "https://v6.ident.me")


def _first_answer(sources, version: int, timeout: float) -> str | None:
    http = session()
    for url in sources:
        try:
            text = http.get(url, timeout=timeout).text.strip()
            if ipaddress.ip_address(text).version == version:
                return text
        except (requests.RequestException, ValueError):
            continue
    return None


def my_ip(timeout: float = 6) -> dict:
    ipv4 = _first_answer(IPV4_SOURCES, 4, timeout)
    # IPv6 is optional; a short timeout keeps IPv4-only networks snappy.
    ipv6 = _first_answer(IPV6_SOURCES, 6, min(timeout, 4))
    if not ipv4 and not ipv6:
        raise StalkerError("myip.failed", reason="no response from any IP service")
    return {"ipv4": ipv4, "ipv6": ipv6}
