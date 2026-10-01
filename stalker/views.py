"""Render lookup results with translated labels."""

from __future__ import annotations

from stalker import ui
from stalker.core import ip_lookup, username
from stalker.i18n import t, yes_no

_BOOL_IP_FIELDS = {"is_eu", "tz_dst"}


def show_ip(data: dict) -> None:
    ui.section(t("ip.title"))
    rows = []
    for key in ip_lookup.FIELDS:
        value = data.get(key)
        if key in _BOOL_IP_FIELDS:
            value = yes_no(value)
        elif isinstance(value, list):
            value = ", ".join(value)
        rows.append((t(f"ip.{key}"), value))
    rows.append((t("ip.source"), data.get("source")))
    ui.kv_table(rows)
    print()
    ui.note(t("ip.note"))


def show_my_ip(data: dict) -> None:
    ui.section(t("myip.title"))
    ui.kv_table(
        [
            (t("myip.ipv4"), data.get("ipv4") or t("myip.unavailable")),
            (t("myip.ipv6"), data.get("ipv6") or t("myip.unavailable")),
        ]
    )


def show_phone(data: dict) -> None:
    ui.section(t("phone.title"))
    ui.kv_table(
        [
            (t("phone.input"), data["input"]),
            (t("phone.location"), data["location"]),
            (t("phone.region_code"), data["region_code"]),
            (t("phone.timezones"), ", ".join(data["timezones"])),
            (t("phone.carrier"), data["carrier"]),
            (t("phone.valid"), yes_no(data["valid"])),
            (t("phone.possible"), yes_no(data["possible"])),
            (t("phone.type"), t(f"phone.type.{data['type']}")),
            (t("phone.country_code"), data["country_code"]),
            (t("phone.national_number"), data["national_number"]),
            (t("phone.international"), data["international"]),
            (t("phone.national"), data["national"]),
            (t("phone.mobile_dialing"), data["mobile_dialing"]),
            (t("phone.e164"), data["e164"]),
        ]
    )
    print()
    ui.note(t("phone.note"))


_STATUS_STYLE = {
    username.FOUND: ("user.found", ui.green, "+"),
    username.NOT_FOUND: ("user.not_found", ui.red, "-"),
    username.UNKNOWN: ("user.unknown", ui.yellow, "?"),
}


def show_username(name: str, results: list[dict], found_only: bool = False) -> None:
    ui.section(f"{t('user.title')}: {name}")
    width = max(len(r["site"]) for r in results)
    label_width = max(len(t(key)) for key, _, _ in _STATUS_STYLE.values())
    for r in results:
        if found_only and r["status"] != username.FOUND:
            continue
        key, color, mark = _STATUS_STYLE[r["status"]]
        print(f"  {color(f'[{mark}]')} {r['site'].ljust(width)}  "
              f"{color(t(key).ljust(label_width))}  {ui.dim(r['url'])}")

    counts = {s: sum(1 for r in results if r["status"] == s) for s in _STATUS_STYLE}
    print()
    print("  " + ui.bold(t("user.summary", found=counts[username.FOUND],
                             not_found=counts[username.NOT_FOUND],
                             unknown=counts[username.UNKNOWN])))
    if counts[username.UNKNOWN]:
        ui.note(t("user.unknown_hint"))
