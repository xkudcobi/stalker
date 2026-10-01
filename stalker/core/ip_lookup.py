"""IP geolocation via ipwho.is, with ip-api.com as a fallback."""

from __future__ import annotations

import ipaddress
from datetime import datetime, timedelta, timezone

import requests

from stalker.net import DEFAULT_TIMEOUT, StalkerError, session

PRIMARY = "https://ipwho.is/{ip}"
FALLBACK = (
    "http://ip-api.com/json/{ip}?fields=status,message,query,continent,continentCode,"
    "country,countryCode,region,regionName,city,zip,lat,lon,timezone,offset,isp,org,as"
)

# Order of fields in the result; the UI uses the same keys for its labels.
FIELDS = (
    "ip", "type", "continent", "continent_code", "country", "country_code", "flag",
    "capital", "borders", "calling_code", "is_eu", "region", "region_code", "city",
    "postal", "latitude", "longitude", "maps", "osm", "asn", "org", "isp", "domain",
    "tz_id", "tz_abbr", "tz_dst", "tz_offset", "tz_utc", "tz_time",
)


def validate(ip: str) -> str:
    """Return the normalised address, or raise StalkerError for bad / non-public input."""
    try:
        addr = ipaddress.ip_address(ip.strip())
    except ValueError:
        raise StalkerError("ip.invalid", value=ip) from None
    if not addr.is_global:
        raise StalkerError("ip.private", value=ip)
    return str(addr)


def _map_links(lat, lon) -> tuple[str | None, str | None]:
    if lat is None or lon is None:
        return None, None
    return (
        f"https://www.google.com/maps?q={lat},{lon}",
        f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}",
    )


def _from_ipwhois(data: dict) -> dict:
    conn = data.get("connection") or {}
    tz = data.get("timezone") or {}
    lat, lon = data.get("latitude"), data.get("longitude")
    maps, osm = _map_links(lat, lon)
    borders = data.get("borders")
    return {
        "ip": data.get("ip"),
        "type": data.get("type"),
        "continent": data.get("continent"),
        "continent_code": data.get("continent_code"),
        "country": data.get("country"),
        "country_code": data.get("country_code"),
        "flag": (data.get("flag") or {}).get("emoji"),
        "capital": data.get("capital"),
        "borders": borders.replace(",", ", ") if isinstance(borders, str) else borders,
        "calling_code": f"+{data['calling_code']}" if data.get("calling_code") else None,
        "is_eu": data.get("is_eu"),
        "region": data.get("region"),
        "region_code": data.get("region_code"),
        "city": data.get("city"),
        "postal": data.get("postal"),
        "latitude": lat,
        "longitude": lon,
        "maps": maps,
        "osm": osm,
        "asn": f"AS{conn['asn']}" if conn.get("asn") else None,
        "org": conn.get("org"),
        "isp": conn.get("isp"),
        "domain": conn.get("domain"),
        "tz_id": tz.get("id"),
        "tz_abbr": tz.get("abbr"),
        "tz_dst": tz.get("is_dst"),
        "tz_offset": tz.get("offset"),
        "tz_utc": tz.get("utc"),
        "tz_time": tz.get("current_time") or _local_time(tz.get("offset")),
        "source": "ipwho.is",
    }


def _from_ipapi(data: dict) -> dict:
    lat, lon = data.get("lat"), data.get("lon")
    maps, osm = _map_links(lat, lon)
    ip = data.get("query")
    asn = (data.get("as") or "").split(" ", 1)[0] or None
    offset = data.get("offset")
    result = dict.fromkeys(FIELDS)
    result.update(
        {
            "ip": ip,
            "type": f"IPv{ipaddress.ip_address(ip).version}" if ip else None,
            "continent": data.get("continent"),
            "continent_code": data.get("continentCode"),
            "country": data.get("country"),
            "country_code": data.get("countryCode"),
            "region": data.get("regionName"),
            "region_code": data.get("region"),
            "city": data.get("city"),
            "postal": data.get("zip"),
            "latitude": lat,
            "longitude": lon,
            "maps": maps,
            "osm": osm,
            "asn": asn,
            "org": data.get("org"),
            "isp": data.get("isp"),
            "tz_id": data.get("timezone"),
            "tz_offset": offset,
            "tz_utc": _format_utc(offset),
            "tz_time": _local_time(offset),
            "source": "ip-api.com",
        }
    )
    return result


def _format_utc(offset) -> str | None:
    if offset is None:
        return None
    sign = "+" if offset >= 0 else "-"
    minutes = abs(int(offset)) // 60
    return f"{sign}{minutes // 60:02d}:{minutes % 60:02d}"


def _local_time(offset) -> str | None:
    if offset is None:
        return None
    now = datetime.now(timezone(timedelta(seconds=int(offset))))
    return now.strftime("%Y-%m-%d %H:%M:%S")


def lookup(ip: str | None = None, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Look up `ip` (or the caller's own address when empty) and return a flat dict."""
    target = validate(ip) if ip and ip.strip() else ""
    http = session()
    reason = "unknown error"

    try:
        resp = http.get(PRIMARY.format(ip=target), timeout=timeout)
        data = resp.json()
        if data.get("success"):
            return _from_ipwhois(data)
        reason = data.get("message") or f"HTTP {resp.status_code}"
    except (requests.RequestException, ValueError) as exc:
        reason = str(exc)

    try:
        resp = http.get(FALLBACK.format(ip=target), timeout=timeout)
        data = resp.json()
        if data.get("status") == "success":
            return _from_ipapi(data)
        reason = data.get("message") or reason
    except (requests.RequestException, ValueError) as exc:
        reason = str(exc)

    raise StalkerError("ip.failed", reason=reason)
