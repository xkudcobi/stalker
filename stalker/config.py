"""Tiny persistent settings file (~/.config/stalker/config.json)."""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {"lang": None, "region": "TR"}


def _path() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "stalker" / "config.json"


def _load() -> dict:
    try:
        return {**DEFAULTS, **json.loads(_path().read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return dict(DEFAULTS)


def get(key: str):
    return _load().get(key)


def set(key: str, value) -> None:  # noqa: A001 - mirrors get()
    data = _load()
    data[key] = value
    try:
        path = _path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass  # settings are a convenience; never fail a lookup over them
